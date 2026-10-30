import os
import unittest

from tests.helpers import make_client

TABLES = {
    "/api/addresses": 12,
    "/api/owners": 14,
    "/api/panel-types": 10,
    "/api/battery-types": 10,
    "/api/energy-prices": 15,
    "/api/stations": 12,
    "/api/station-owners": 16,
    "/api/panels": 15,
    "/api/batteries": 12,
    "/api/panel-generation": 15,
    "/api/panel-tilt-log": 12,
    "/api/battery-charge-log": 15,
    "/api/energy-sales": 15,
}


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self.client, self.db_path = make_client()

    def tearDown(self):
        os.remove(self.db_path)

    def call(self, method, url, expected, body=None):
        response = getattr(self.client, method)(url, json=body) if body is not None else getattr(self.client, method)(url)
        self.assertEqual(response.status_code, expected, f"{method.upper()} {url} -> {response.get_json()}")
        return response.get_json()


class ReadTests(ApiTestCase):
    def test_all_tables_are_listed(self):
        for url, count in TABLES.items():
            with self.subTest(url=url):
                self.assertEqual(len(self.call("get", url, 200)), count)

    def test_get_one_and_404(self):
        self.assertEqual(self.call("get", "/api/stations/1", 200)["station_name"], "Дах-Львів-1")
        self.assertEqual(self.call("get", "/api/station-owners/2/3", 200)["ownership_share"], 40.0)
        self.assertEqual(self.call("get", "/api/stations/999", 404)["error"], "NotFoundError")

    def test_pagination(self):
        self.assertEqual(len(self.call("get", "/api/owners?limit=3&offset=2", 200)), 3)
        self.call("get", "/api/owners?limit=abc", 400)

    def test_panel_dto_has_usage_days_and_bool(self):
        panel = self.call("get", "/api/panels/1", 200)
        self.assertGreater(panel["usage_days"], 1000)
        self.assertIs(self.call("get", "/api/panel-types/2", 200)["is_adjustable"], True)

    def test_health_and_routes(self):
        self.call("get", "/api/health", 200)
        self.assertGreater(len(self.call("get", "/api/routes", 200)), 50)
        self.assertEqual(self.client.get("/").status_code, 200)


class CrudTests(ApiTestCase):
    def test_address_crud(self):
        created = self.call("post", "/api/addresses", 201, {
            "country": "Україна", "region": "Львівська обл.", "city": "Стрий",
            "street": "вул. Нова", "building_number": "1", "latitude": 49.26, "longitude": 23.85})
        address_id = created["address_id"]
        self.assertEqual(created["city"], "Стрий")
        updated = self.call("put", f"/api/addresses/{address_id}", 200, {"street": "вул. Стара"})
        self.assertEqual(updated["street"], "вул. Стара")
        self.assertEqual(updated["city"], "Стрий")
        self.call("delete", f"/api/addresses/{address_id}", 200)
        self.call("get", f"/api/addresses/{address_id}", 404)

    def test_full_chain_create_and_delete(self):
        address = self.call("post", "/api/addresses", 201, {
            "country": "Україна", "region": "Київська обл.", "city": "Бровари",
            "street": "вул. Київська", "building_number": "9"})
        station = self.call("post", "/api/stations", 201, {
            "address_id": address["address_id"], "station_name": "Тест-станція",
            "installation_date": "2026-01-15", "grid_connection_id": "GRID-TEST-1"})
        self.assertEqual(station["status"], "active")
        owner = self.call("post", "/api/owners", 201, {
            "first_name": "Тест", "last_name": "Тестенко", "phone": "+380991112233", "email": "t@example.com"})
        link = self.call("post", "/api/station-owners", 201, {
            "station_id": station["station_id"], "owner_id": owner["owner_id"],
            "ownership_share": 100, "since_date": "2026-01-15"})
        self.assertEqual(link["ownership_share"], 100.0)
        panel = self.call("post", "/api/panels", 201, {
            "station_id": station["station_id"], "panel_type_id": 2,
            "serial_number": "SN-TEST-1", "installation_date": "2026-01-15"})
        self.assertEqual(panel["current_tilt_angle"], 30.0)
        battery = self.call("post", "/api/batteries", 201, {
            "station_id": station["station_id"], "battery_type_id": 1,
            "serial_number": "SN-TEST-B1", "installation_date": "2026-01-15"})
        self.call("delete", f"/api/batteries/{battery['battery_id']}", 200)
        self.call("delete", f"/api/station-owners/{station['station_id']}/{owner['owner_id']}", 200)
        self.call("delete", f"/api/stations/{station['station_id']}", 200)
        self.call("get", f"/api/panels/{panel['panel_id']}", 404)
        self.call("delete", f"/api/owners/{owner['owner_id']}", 200)
        self.call("delete", f"/api/addresses/{address['address_id']}", 200)

    def test_update_station_owner_link(self):
        updated = self.call("put", "/api/station-owners/2/2", 200, {"ownership_share": 55})
        self.assertEqual(updated["ownership_share"], 55.0)
        self.call("put", "/api/station-owners/2/2", 400, {"ownership_share": 70})

    def test_partial_updates_use_values_loaded_from_db(self):
        link = self.call("put", "/api/station-owners/2/2", 200, {"since_date": "2021-10-01"})
        self.assertEqual((link["ownership_share"], link["since_date"]), (60.0, "2021-10-01"))
        charge = self.call("put", "/api/battery-charge-log/1", 200, {"reading_datetime": "2026-10-21 00:30:00"})
        self.assertEqual(charge["charge_level_kwh"], 8.1)
        charge = self.call("put", "/api/battery-charge-log/1", 200, {"charge_level_pct": 40})
        self.assertEqual(charge["charge_level_kwh"], 5.4)
        self.call("put", "/api/battery-charge-log/1", 400, {"charge_level_kwh": 13})
        generation = self.call("put", "/api/panel-generation/1", 200, {"generated_kwh": 0.3})
        self.assertEqual(generation["generated_kwh"], 0.3)
        self.call("put", "/api/panel-generation/1", 400, {"reading_datetime": "2000-01-01 10:00:00"})
        sale = self.call("put", "/api/energy-sales/1", 200, {"energy_kwh": 2})
        self.assertEqual(sale["total_amount"], 6.9)
        self.call("put", "/api/panels/1", 200, {"serial_number": "SN-PNL-0001X"})
        self.call("put", "/api/panels/1", 400, {"decommission_date": "2020-01-01"})
        self.call("put", "/api/panel-types/1", 200, {"warranty_years": 30})
        self.call("put", "/api/battery-types/1", 200, {"cycle_life": 5500})
        self.call("put", "/api/energy-prices/1", 200, {"price_per_kwh": 2.2})
        self.call("put", "/api/addresses/1", 200, {"latitude": 50.0})

    def test_patch_works_like_put(self):
        self.assertEqual(self.call("patch", "/api/stations/9", 200, {"status": "active"})["status"], "active")

    def test_update_nonexistent_is_404(self):
        self.call("put", "/api/owners/999", 404, {"first_name": "X"})
        self.call("delete", "/api/owners/999", 404)


class RelationTests(ApiTestCase):
    def test_many_to_one_address_to_stations(self):
        data = self.call("get", "/api/addresses/1/stations", 200)
        self.assertEqual(data["address"]["city"], "Львів")
        self.assertEqual([s["station_id"] for s in data["stations"]], [1])

    def test_many_to_one_for_every_city(self):
        data = self.call("get", "/api/addresses/with-stations", 200)
        self.assertEqual(len(data), 12)
        self.assertTrue(all(len(item["stations"]) == 1 for item in data))
        self.assertIn("city", data[0])

    def test_many_to_one_station_children(self):
        panels = self.call("get", "/api/stations/1/panels", 200)
        self.assertEqual({p["panel_id"] for p in panels["panels"]}, {1, 2})
        self.assertEqual(len(self.call("get", "/api/stations/1/batteries", 200)["batteries"]), 1)
        self.assertEqual(len(self.call("get", "/api/stations/1/sales", 200)["sales"]), 2)
        grouped = self.call("get", "/api/stations/with-panels", 200)
        self.assertEqual(sum(len(s["panels"]) for s in grouped), 15)

    def test_many_to_one_types_and_logs(self):
        self.assertEqual(len(self.call("get", "/api/panel-types/1/panels", 200)["panels"]), 3)
        self.assertEqual(sum(len(t["panels"]) for t in self.call("get", "/api/panel-types/with-panels", 200)), 15)
        self.assertEqual(len(self.call("get", "/api/battery-types/2/batteries", 200)["batteries"]), 2)
        self.assertEqual(len(self.call("get", "/api/panels/1/generation", 200)["generation"]), 15)
        self.assertEqual(len(self.call("get", "/api/panels/2/tilt-log", 200)["tilt_log"]), 2)
        self.assertEqual(len(self.call("get", "/api/batteries/1/charge-log", 200)["charge_log"]), 15)
        self.assertEqual(len(self.call("get", "/api/energy-prices/9/sales", 200)["sales"]), 4)
        self.call("get", "/api/addresses/999/stations", 404)

    def test_many_to_many_owners_of_station(self):
        data = self.call("get", "/api/stations/2/owners", 200)
        self.assertEqual(data["station"]["station_name"], "Сад-Київ-1")
        self.assertEqual({(o["owner_id"], o["ownership_share"]) for o in data["owners"]}, {(2, 60.0), (3, 40.0)})
        self.assertNotIn("station_id", data["owners"][0])

    def test_many_to_many_stations_of_owner(self):
        data = self.call("get", "/api/owners/1/stations", 200)
        self.assertEqual({s["station_id"] for s in data["stations"]}, {1, 4})
        self.assertEqual({s["station_id"] for s in self.call("get", "/api/owners/9/stations", 200)["stations"]}, {7, 12})
        self.call("get", "/api/owners/999/stations", 404)

    def test_many_to_many_for_every_subject(self):
        stations = self.call("get", "/api/stations/with-owners", 200)
        self.assertEqual(len(stations), 12)
        self.assertEqual(sum(len(s["owners"]) for s in stations), 16)
        owners = self.call("get", "/api/owners/with-stations", 200)
        self.assertEqual(len(owners), 14)
        self.assertEqual(sum(len(o["stations"]) for o in owners), 16)


class BusinessRuleTests(ApiTestCase):
    def test_validation_errors(self):
        self.call("post", "/api/addresses", 400, {"city": "Тільки місто"})
        self.call("post", "/api/addresses", 400, {"country": "A", "region": "B", "city": "C",
                                                  "street": "D", "building_number": "1", "zip": "1"})
        self.call("post", "/api/stations", 400, {"address_id": 1, "station_name": "X", "installation_date": "21-10-2026"})
        self.call("post", "/api/stations", 400, {"address_id": 999, "station_name": "X", "installation_date": "2026-01-01"})
        self.call("post", "/api/stations", 400, {"address_id": 1, "station_name": "X",
                                                 "installation_date": "2026-01-01", "status": "broken"})
        self.call("post", "/api/owners", 400, {"first_name": "A", "last_name": "B", "phone": "123"})
        self.assertEqual(self.client.post("/api/owners", data="not json").status_code, 400)

    def test_unique_conflict_is_409(self):
        self.call("post", "/api/owners", 409, {"first_name": "A", "last_name": "B", "phone": "+380671234501"})
        self.call("post", "/api/station-owners", 409, {"station_id": 1, "owner_id": 1,
                                                       "ownership_share": 0.5, "since_date": "2022-05-10"})

    def test_cannot_delete_referenced_row(self):
        self.assertEqual(self.call("delete", "/api/addresses/1", 409)["error"], "ConflictError")
        self.call("delete", "/api/panel-types/1", 409)
        self.call("get", "/api/addresses/1", 200)

    def test_ownership_share_total_limit(self):
        self.call("post", "/api/station-owners", 400, {"station_id": 2, "owner_id": 4,
                                                       "ownership_share": 10, "since_date": "2022-01-01"})
        self.call("post", "/api/station-owners", 400, {"station_id": 3, "owner_id": 5,
                                                       "ownership_share": 150, "since_date": "2022-01-01"})

    def test_generation_cannot_exceed_nominal_power(self):
        self.call("post", "/api/panel-generation", 400, {"panel_id": 1, "reading_datetime": "2026-10-22 12:00:00",
                                                         "generated_kwh": 0.9})
        created = self.call("post", "/api/panel-generation", 201, {"panel_id": 1, "reading_datetime": "2026-10-22 12:00:00",
                                                                   "generated_kwh": 0.41})
        self.assertEqual(created["generated_kwh"], 0.41)

    def test_tilt_only_for_adjustable_panels_and_updates_panel(self):
        self.call("post", "/api/panel-tilt-log", 400, {"panel_id": 1, "change_datetime": "2026-10-22 10:00:00",
                                                       "tilt_angle": 20})
        self.call("post", "/api/panel-tilt-log", 400, {"panel_id": 2, "change_datetime": "2026-10-22 10:00:00",
                                                       "tilt_angle": 120})
        self.call("post", "/api/panel-tilt-log", 201, {"panel_id": 2, "change_datetime": "2026-10-22 10:00:00",
                                                       "tilt_angle": 15})
        self.assertEqual(self.call("get", "/api/panels/2", 200)["current_tilt_angle"], 15.0)
        self.call("post", "/api/panel-tilt-log", 201, {"panel_id": 2, "change_datetime": "2026-10-20 10:00:00",
                                                       "tilt_angle": 40})
        self.assertEqual(self.call("get", "/api/panels/2", 200)["current_tilt_angle"], 15.0)

    def test_charge_kwh_is_calculated_and_checked(self):
        created = self.call("post", "/api/battery-charge-log", 201, {
            "battery_id": 1, "reading_datetime": "2026-10-22 00:00:00", "charge_level_pct": 50})
        self.assertEqual(created["charge_level_kwh"], 6.75)
        self.call("post", "/api/battery-charge-log", 400, {
            "battery_id": 1, "reading_datetime": "2026-10-22 01:00:00", "charge_level_pct": 120})
        self.call("post", "/api/battery-charge-log", 400, {
            "battery_id": 1, "reading_datetime": "2026-10-22 01:00:00", "charge_level_pct": 50,
            "charge_level_kwh": 12})

    def test_sale_price_and_total_are_calculated(self):
        sale = self.call("post", "/api/energy-sales", 201, {
            "station_id": 1, "sale_datetime": "2026-10-21 10:30:00", "energy_kwh": 2})
        self.assertEqual(sale["price_id"], 11)
        self.assertEqual(sale["total_amount"], 5.9)
        updated = self.call("put", f"/api/energy-sales/{sale['sale_id']}", 200, {"energy_kwh": 3})
        self.assertEqual(updated["total_amount"], 8.85)
        moved = self.call("put", f"/api/energy-sales/{sale['sale_id']}", 200, {"sale_datetime": "2026-10-21 12:15:00"})
        self.assertEqual(moved["price_id"], 13)
        self.assertEqual(moved["total_amount"], 7.5)

    def test_sale_rejections(self):
        self.call("post", "/api/energy-sales", 400, {"station_id": 4, "sale_datetime": "2026-10-21 10:00:00",
                                                     "energy_kwh": 1})
        self.call("post", "/api/energy-sales", 400, {"station_id": 1, "sale_datetime": "2026-10-25 10:00:00",
                                                     "energy_kwh": 1})
        self.call("post", "/api/energy-sales", 400, {"station_id": 1, "sale_datetime": "2026-10-21 10:00:00",
                                                     "energy_kwh": 1, "price_id": 3})
        self.call("post", "/api/energy-sales", 400, {"station_id": 1, "sale_datetime": "2026-10-21 10:00:00",
                                                     "energy_kwh": -1})

    def test_failed_request_does_not_change_data(self):
        self.call("post", "/api/energy-sales", 400, {"station_id": 4, "sale_datetime": "2026-10-21 10:00:00",
                                                     "energy_kwh": 1})
        self.assertEqual(len(self.call("get", "/api/energy-sales", 200)), 15)


if __name__ == "__main__":
    unittest.main()
