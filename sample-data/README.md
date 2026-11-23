# Sample data

Everything here is made up, so every tool runs without exposing anyone.

- **People** are historical computing and maths pioneers used as obvious placeholders. Their roles,
  teams and scores are invented.
- **Example College**, its campus, address and phone number are fictional, and `example.org` is a
  domain reserved for examples.
- **Pictures** are drawn by code in [`tools/make_demo_assets.py`](../tools/make_demo_assets.py). No
  real photo, logo or signature is stored in this repository.

[`tools/privacy_check.py`](../tools/privacy_check.py) runs in CI and fails if a real-looking email,
phone number, private link or key appears, or if a sample list holds a name that is not in
[`fictional-people.txt`](fictional-people.txt).
