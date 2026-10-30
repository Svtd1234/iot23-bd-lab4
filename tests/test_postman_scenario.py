import importlib.util
import json
import os
import re
import unittest

from tests.helpers import make_client

SPEC_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "postman", "build_collection.py")
spec = importlib.util.spec_from_file_location("build_collection", SPEC_PATH)
build_collection = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_collection)

PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")


def render(text, variables):
    """Як Postman: {{var}} підставляється в текст запиту дослівно."""
    return PLACEHOLDER.sub(lambda m: str(variables.get(m.group(1), m.group(0))), text)


class PostmanScenarioTest(unittest.TestCase):
    def run_collection(self, client, collection):
        variables = {"baseUrl": ""}
        for folder in collection["item"]:
            for item in folder["item"]:
                request = item["request"]
                url = render(request["url"]["raw"], variables)
                kwargs = {}
                if "body" in request:
                    kwargs["data"] = render(request["body"]["raw"], variables).encode("utf-8")
                    kwargs["content_type"] = "application/json"
                response = client.open(url, method=request["method"], **kwargs)
                script = "\n".join(item["event"][0]["script"]["exec"])
                expected = int(re.search(r"have\.status\((\d+)\)", script).group(1))
                self.assertEqual(response.status_code, expected,
                                 f"[{folder['name']}] {item['name']}: {request['method']} {url} -> {response.get_json()}")
                for var, key in re.findall(r'collectionVariables\.set\("(\w+)", json\.(\w+)\)', script):
                    variables[var] = response.get_json()[key]

    def test_saved_collection_file_runs_twice_without_errors(self):
        with open(build_collection.OUT, encoding="utf-8") as f:
            collection = json.load(f)
        self.assertEqual(collection, build_collection.build())
        client, path = make_client()
        try:
            self.run_collection(client, collection)
            self.run_collection(client, collection)
            self.assertEqual(len(client.get("/api/stations").get_json()), 12)
            self.assertEqual(len(client.get("/api/panel-types").get_json()), 10)
        finally:
            os.remove(path)

    def test_numeric_ids_are_not_quoted_in_bodies(self):
        for folder in build_collection.build()["item"]:
            for item in folder["item"]:
                body = item["request"].get("body", {}).get("raw", "")
                self.assertNotRegex(body, r'"\{\{')


if __name__ == "__main__":
    unittest.main()
