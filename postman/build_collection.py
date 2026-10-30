import json
import os
import re

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "solar_monitoring.postman_collection.json")


def step(name, method, path, body=None, status=200, save=None):
    return {"name": name, "method": method, "path": path, "body": body, "status": status, "save": save or {}}


READ = [
    step(f"GET {name}", "GET", f"/api/{url}")
    for name, url in [
        ("addresses", "addresses"), ("owners", "owners"), ("panel-types", "panel-types"),
        ("battery-types", "battery-types"), ("energy-prices", "energy-prices"), ("stations", "stations"),
        ("station-owners (M:N)", "station-owners"), ("panels", "panels"), ("batteries", "batteries"),
        ("panel-generation", "panel-generation"), ("panel-tilt-log", "panel-tilt-log"),
        ("battery-charge-log", "battery-charge-log"), ("energy-sales", "energy-sales"),
    ]
] + [
    step("GET станція за id", "GET", "/api/stations/1"),
    step("GET запис зі складеним ключем (станція 2, власник 3)", "GET", "/api/station-owners/2/3"),
    step("GET пагінація (limit=3&offset=2)", "GET", "/api/owners?limit=3&offset=2"),
    step("GET неіснуючий запис -> 404", "GET", "/api/stations/999", status=404),
]

INSERT = [
    step("POST address", "POST", "/api/addresses", {
        "country": "Україна", "region": "Львівська обл.", "city": "Стрий", "street": "вул. Нова",
        "building_number": "1", "postal_code": "82400", "latitude": 49.26, "longitude": 23.85},
        201, {"address_id": "address_id"}),
    step("POST owner", "POST", "/api/owners", {
        "first_name": "Тест", "last_name": "Тестенко", "phone": "+380991112233", "email": "test@example.com"},
        201, {"owner_id": "owner_id"}),
    step("POST panel-type", "POST", "/api/panel-types", {
        "manufacturer": "TestSolar", "model": "TS-500", "nominal_power_w": 500, "is_adjustable": True,
        "warranty_years": 15}, 201, {"panel_type_id": "panel_type_id"}),
    step("POST battery-type", "POST", "/api/battery-types", {
        "manufacturer": "TestBattery", "model": "TB-10", "capacity_kwh": 10, "cycle_life": 5000,
        "warranty_years": 10}, 201, {"battery_type_id": "battery_type_id"}),
    step("POST energy-price", "POST", "/api/energy-prices", {
        "price_datetime": "2026-10-22 10:00:00", "price_per_kwh": 3.0}, 201, {"price_id": "price_id"}),
    step("POST station", "POST", "/api/stations", {
        "address_id": "{{address_id}}", "station_name": "Тест-станція", "installation_date": "2026-01-15",
        "grid_connection_id": "GRID-TEST-1", "status": "active"}, 201, {"station_id": "station_id"}),
    step("POST station-owner (M:N)", "POST", "/api/station-owners", {
        "station_id": "{{station_id}}", "owner_id": "{{owner_id}}", "ownership_share": 100,
        "since_date": "2026-01-15"}, 201),
    step("POST panel", "POST", "/api/panels", {
        "station_id": "{{station_id}}", "panel_type_id": "{{panel_type_id}}", "serial_number": "SN-TEST-0001",
        "installation_date": "2026-01-15"}, 201, {"panel_id": "panel_id"}),
    step("POST battery", "POST", "/api/batteries", {
        "station_id": "{{station_id}}", "battery_type_id": "{{battery_type_id}}", "serial_number": "SN-TEST-B001",
        "installation_date": "2026-01-15"}, 201, {"battery_id": "battery_id"}),
    step("POST panel-generation", "POST", "/api/panel-generation", {
        "panel_id": "{{panel_id}}", "reading_datetime": "2026-10-22 12:00:00", "generated_kwh": 0.45},
        201, {"generation_id": "generation_id"}),
    step("POST panel-tilt-log", "POST", "/api/panel-tilt-log", {
        "panel_id": "{{panel_id}}", "change_datetime": "2026-10-22 10:00:00", "tilt_angle": 25},
        201, {"tilt_log_id": "tilt_log_id"}),
    step("POST battery-charge-log (кВт·год рахується автоматично)", "POST", "/api/battery-charge-log", {
        "battery_id": "{{battery_id}}", "reading_datetime": "2026-10-22 10:00:00", "charge_level_pct": 50},
        201, {"charge_log_id": "charge_log_id"}),
    step("POST energy-sale (ціна й сума рахуються автоматично)", "POST", "/api/energy-sales", {
        "station_id": "{{station_id}}", "sale_datetime": "2026-10-22 10:30:00", "energy_kwh": 2},
        201, {"sale_id": "sale_id"}),
    step("POST помилка валідації -> 400", "POST", "/api/addresses", {"city": "Тільки місто"}, 400),
    step("POST дублікат телефону -> 409", "POST", "/api/owners", {
        "first_name": "A", "last_name": "B", "phone": "+380991112233"}, 409),
]

UPDATE = [
    step("PUT address (часткове оновлення)", "PUT", "/api/addresses/{{address_id}}", {"street": "вул. Оновлена"}),
    step("PUT owner", "PUT", "/api/owners/{{owner_id}}", {"email": "new@example.com"}),
    step("PUT station", "PUT", "/api/stations/{{station_id}}", {"status": "maintenance"}),
    step("PATCH station", "PATCH", "/api/stations/{{station_id}}", {"status": "active"}),
    step("PUT station-owner (складений ключ)", "PUT", "/api/station-owners/{{station_id}}/{{owner_id}}",
         {"ownership_share": 80}),
    step("PUT panel", "PUT", "/api/panels/{{panel_id}}", {"current_tilt_angle": 28}),
    step("PUT energy-sale (сума перераховується)", "PUT", "/api/energy-sales/{{sale_id}}", {"energy_kwh": 3}),
    step("PUT неіснуючий запис -> 404", "PUT", "/api/owners/99999", {"first_name": "X"}, 404),
    step("PUT перевищення 100% часток -> 400", "PUT", "/api/station-owners/2/2", {"ownership_share": 90}, 400),
]

MANY_TO_ONE = [
    step("Для кожного міста — станції в ньому (/addresses/with-stations)", "GET", "/api/addresses/with-stations"),
    step("Станції конкретної адреси", "GET", "/api/addresses/1/stations"),
    step("Для кожної станції — її панелі", "GET", "/api/stations/with-panels"),
    step("Панелі станції", "GET", "/api/stations/1/panels"),
    step("Батареї станції", "GET", "/api/stations/1/batteries"),
    step("Продажі станції", "GET", "/api/stations/1/sales"),
    step("Для кожного типу панелі — панелі цього типу", "GET", "/api/panel-types/with-panels"),
    step("Панелі типу", "GET", "/api/panel-types/1/panels"),
    step("Батареї типу", "GET", "/api/battery-types/2/batteries"),
    step("Генерація панелі по годинах", "GET", "/api/panels/1/generation"),
    step("Журнал кутів нахилу панелі", "GET", "/api/panels/2/tilt-log"),
    step("Журнал заряду батареї", "GET", "/api/batteries/1/charge-log"),
    step("Продажі за ціною", "GET", "/api/energy-prices/9/sales"),
]

MANY_TO_MANY = [
    step("Для кожної станції — усі її власники (/stations/with-owners)", "GET", "/api/stations/with-owners"),
    step("Для кожного власника — усі його станції (/owners/with-stations)", "GET", "/api/owners/with-stations"),
    step("Власники станції 2", "GET", "/api/stations/2/owners"),
    step("Станції власника 1", "GET", "/api/owners/1/stations"),
    step("Власники щойно створеної станції", "GET", "/api/stations/{{station_id}}/owners"),
]

DELETE = [
    step("DELETE energy-sale", "DELETE", "/api/energy-sales/{{sale_id}}"),
    step("DELETE battery-charge-log", "DELETE", "/api/battery-charge-log/{{charge_log_id}}"),
    step("DELETE panel-tilt-log", "DELETE", "/api/panel-tilt-log/{{tilt_log_id}}"),
    step("DELETE panel-generation", "DELETE", "/api/panel-generation/{{generation_id}}"),
    step("DELETE battery", "DELETE", "/api/batteries/{{battery_id}}"),
    step("DELETE panel", "DELETE", "/api/panels/{{panel_id}}"),
    step("DELETE station-owner (складений ключ)", "DELETE", "/api/station-owners/{{station_id}}/{{owner_id}}"),
    step("DELETE station", "DELETE", "/api/stations/{{station_id}}"),
    step("DELETE owner", "DELETE", "/api/owners/{{owner_id}}"),
    step("DELETE address", "DELETE", "/api/addresses/{{address_id}}"),
    step("DELETE panel-type", "DELETE", "/api/panel-types/{{panel_type_id}}"),
    step("DELETE battery-type", "DELETE", "/api/battery-types/{{battery_type_id}}"),
    step("DELETE energy-price", "DELETE", "/api/energy-prices/{{price_id}}"),
    step("DELETE адреси, на яку посилаються станції -> 409", "DELETE", "/api/addresses/1", status=409),
    step("GET видаленої станції -> 404", "GET", "/api/stations/{{station_id}}", status=404),
]

FOLDERS = [
    ("1. Вивід даних з таблиць", READ),
    ("2. Вставка даних (POST)", INSERT),
    ("3. Оновлення даних (PUT/PATCH)", UPDATE),
    ("4. Вивід зі сторони зв'язку M:1", MANY_TO_ONE),
    ("5. Вивід зі стикувальної таблиці M:M", MANY_TO_MANY),
    ("6. Видалення даних (DELETE)", DELETE),
]


def _item(s):
    raw_path = s["path"]
    path, _, query = raw_path.partition("?")
    url = {
        "raw": "{{baseUrl}}" + raw_path,
        "host": ["{{baseUrl}}"],
        "path": [p for p in path.split("/") if p],
    }
    if query:
        url["query"] = [{"key": k, "value": v} for k, v in (q.split("=") for q in query.split("&"))]
    lines = [
        f'pm.test("Статус {s["status"]}", function () {{ pm.response.to.have.status({s["status"]}); }});',
    ]
    if s["save"]:
        lines.append("const json = pm.response.json();")
        for var, key in s["save"].items():
            lines.append(f'pm.collectionVariables.set("{var}", json.{key});')
    request = {"method": s["method"], "header": [], "url": url}
    if s["body"] is not None:
        request["header"].append({"key": "Content-Type", "value": "application/json"})
        raw_body = json.dumps(s["body"], ensure_ascii=False, indent=2)
        raw_body = re.sub(r'"(\{\{\w+\}\})"', r"\1", raw_body)
        request["body"] = {
            "mode": "raw",
            "raw": raw_body,
            "options": {"raw": {"language": "json"}},
        }
    return {
        "name": s["name"],
        "event": [{"listen": "test", "script": {"type": "text/javascript", "exec": lines}}],
        "request": request,
    }


def build():
    return {
        "info": {
            "name": "Solar Monitoring API (лабораторна 4)",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "variable": [{"key": "baseUrl", "value": "http://localhost:5000"}],
        "item": [{"name": name, "item": [_item(s) for s in steps]} for name, steps in FOLDERS],
    }


if __name__ == "__main__":
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(build(), f, ensure_ascii=False, indent=2)
    print("saved", OUT, sum(len(s) for _, s in FOLDERS), "requests")
