import unittest
from app.domain_analyzer import extract_urls_and_domains


class TestURLExtraction(unittest.TestCase):

    def test_basic_url(self):
        text = "Check out this link: https://www.example.com"
        urls, domains = extract_urls_and_domains(text)
        self.assertEqual(urls, ["https://www.example.com"])
        self.assertEqual(domains, ["example.com"])

    def test_www_url(self):
        text = "Visit www.example.com for more info."
        urls, domains = extract_urls_and_domains(text)
        self.assertEqual(urls, ["www.example.com"])
        self.assertEqual(domains, ["example.com"])

    def test_no_protocol_url(self):
        text = "Check out example.com"
        urls, domains = extract_urls_and_domains(text)
        self.assertEqual(urls, ["example.com"])
        self.assertEqual(domains, ["example.com"])

    def test_multiple_urls(self):
        text = "Here are two links: https://www.example.com and http://test.com"
        urls, domains = extract_urls_and_domains(text)
        self.assertEqual(urls, ["https://www.example.com", "http://test.com"])
        self.assertEqual(domains, ["example.com", "test.com"])

    def test_subdomain(self):
        text = "Visit subdomain.example.com"
        urls, domains = extract_urls_and_domains(text)
        self.assertEqual(urls, ["subdomain.example.com"])
        self.assertEqual(domains, ["example.com"])

    def test_url_with_query_params(self):
        text = (
            "Check this out: https://www.example.com?query=test http://test.org?page=1"
        )
        urls, domains = extract_urls_and_domains(text)
        self.assertEqual(
            urls,
            [
                "https://www.example.com?query=test",
                "http://test.org?page=1",
            ],
        )
        self.assertEqual(
            domains,
            [
                "example.com",
                "test.org",
            ],
        )

    def test_ip_address(self):
        text = "Access the server at http://192.168.0.1"
        urls, domains = extract_urls_and_domains(text)
        self.assertEqual(urls, [])
        self.assertEqual(domains, [])

    def test_text_without_url(self):
        text = "This is just regular text without any URL."
        urls, domains = extract_urls_and_domains(text)
        self.assertEqual(urls, [])
        self.assertEqual(domains, [])

    def test_tld_without_protocol(self):
        text = "abc.example.com is a great site!"
        urls, domains = extract_urls_and_domains(text)
        self.assertEqual(urls, ["abc.example.com"])
        self.assertEqual(domains, ["example.com"])

    def test_edge_case_double_dot(self):
        text = "Visit 2.bbc.news.sk or test..com"
        urls, domains = extract_urls_and_domains(text)
        self.assertEqual(urls, ["2.bbc.news.sk"])
        self.assertEqual(domains, ["news.sk"])

    def test_malformed_urls(self):
        text = "Some bad URLs: http://, https://example, and http://test@com or http:///www.example..com."
        urls, domains = extract_urls_and_domains(text)
        self.assertEqual(urls, [])
        self.assertEqual(domains, [])


if __name__ == "__main__":
    unittest.main()
