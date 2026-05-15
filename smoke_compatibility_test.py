import json
import time
import threading
import unittest

import requests


class CompatibilityTest(unittest.TestCase):
    """Regression tests that guard against client-compatibility breakages.

    Each test is named after the production incident it would have caught:
      - test_request_without_content_type_header  → FastAPI 0.132 strict_content_type (HTTP 422)
      - test_request_with_extra_body_fields        → Weaviate Go client extra JSON fields
      - test_concurrent_requests_no_500            → TTLCache race condition (OrderedDict mutation)
      - test_task_type_configs                     → passage / query task_type round-trip
      - test_cached_vector_is_deterministic        → cache correctness after concurrent writes
    """

    def setUp(self):
        self.url = "http://localhost:8000"
        for i in range(100):
            try:
                res = requests.get(self.url + "/.well-known/ready")
                if res.status_code == 204:
                    return
            except Exception as e:
                print(f"Attempt {i}: {e}")
                time.sleep(1)
        raise Exception("service did not start up in time")

    def test_request_without_content_type_header(self):
        """JSON body with no Content-Type header must return 200, not 422.

        FastAPI >= 0.132 introduced strict Content-Type checking by default.
        We disable it (strict_content_type=False) so that clients such as
        Weaviate's shared transformer Go client — which never set the header —
        keep working after a FastAPI version bump.

        requests.post(data=bytes) sends the raw body without adding a
        Content-Type header, mirroring Go's http.NewRequestWithContext with
        no header set. Using json= instead would silently add the header.
        """
        body = json.dumps({"text": "The London Eye is a ferris wheel."}).encode()
        res = requests.post(self.url + "/vectors", data=body)
        self.assertEqual(200, res.status_code, f"Expected 200, got {res.status_code}: {res.text}")
        self.assertGreater(len(res.json()["vector"]), 0)

    def test_request_with_content_type_header(self):
        """JSON body with Content-Type: application/json must return 200.

        Counterpart to test_request_without_content_type_header — ensures
        standard well-behaved clients are unaffected by strict_content_type=False.
        """
        body = json.dumps({"text": "The London Eye is a ferris wheel."}).encode()
        res = requests.post(
            self.url + "/vectors",
            data=body,
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(200, res.status_code, f"Expected 200, got {res.status_code}: {res.text}")
        self.assertGreater(len(res.json()["vector"]), 0)

    def test_request_with_extra_body_fields(self):
        """Extra JSON fields sent by the Weaviate transformer client must be ignored.

        Weaviate's vecRequest struct serialises dims, vector, and error alongside
        text and config. Pydantic must silently discard unknown fields rather than
        returning 422.
        """
        body = {
            "text": "The London Eye is a ferris wheel.",
            "dims": 0,
            "vector": None,
            "error": "",
            "config": {"task_type": "passage"},
        }
        res = requests.post(self.url + "/vectors", json=body)
        self.assertEqual(200, res.status_code, res.text)
        self.assertGreater(len(res.json()["vector"]), 0)

    def test_concurrent_requests_no_500(self):
        """50 concurrent vectorize calls must all succeed.

        Regression for the TTLCache race condition that produced
        'RuntimeError: OrderedDict mutated during iteration' (HTTP 500) when
        the @cached decorator was used without a threading lock.
        """
        texts = [f"Concurrent sentence {i} on a distinct topic." for i in range(50)]
        errors = []

        def vectorize(text):
            try:
                res = requests.post(self.url + "/vectors", json={"text": text})
                if res.status_code != 200:
                    errors.append(f"[{res.status_code}] {res.text}")
            except Exception as exc:
                errors.append(str(exc))

        threads = [threading.Thread(target=vectorize, args=(t,)) for t in texts]
        for th in threads:
            th.start()
        for th in threads:
            th.join()

        self.assertEqual([], errors, f"Concurrent requests failed:\n" + "\n".join(errors))

    def test_task_type_configs(self):
        """Both passage and query task_type values produce a valid vector."""
        text = "The London Eye is a ferris wheel at the River Thames."
        for task_type in ("passage", "query"):
            res = requests.post(
                self.url + "/vectors",
                json={"text": text, "config": {"task_type": task_type}},
            )
            self.assertEqual(200, res.status_code, f"task_type={task_type}: {res.text}")
            self.assertGreater(len(res.json()["vector"]), 0)

    def test_cached_vector_is_deterministic(self):
        """Repeated calls for identical text return bit-identical vectors.

        Validates that the TTLCache returns a stable result after concurrent
        writes and that the lock does not corrupt cached values.
        """
        text = "Determinism check: this sentence must always yield the same vector."
        results = []

        def fetch():
            res = requests.post(self.url + "/vectors", json={"text": text})
            self.assertEqual(200, res.status_code, res.text)
            results.append(res.json()["vector"])

        threads = [threading.Thread(target=fetch) for _ in range(10)]
        for th in threads:
            th.start()
        for th in threads:
            th.join()

        self.assertTrue(all(v == results[0] for v in results), "Vectors diverged across calls")


if __name__ == "__main__":
    unittest.main()
