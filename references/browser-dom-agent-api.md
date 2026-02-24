# Browser DOM Agent API

Base URL: `http://127.0.0.1:8770`

Auth:
- Every POST request must include `token`.

Endpoints:

- `GET /health`
  - Returns liveness.

- `POST /open`
  - Body:
    ```json
    {"token":"YOUR_TOKEN","url":"https://github.com"}
    ```

- `POST /state`
  - Body:
    ```json
    {"token":"YOUR_TOKEN","selectors":["textarea","button:has-text('Commit changes...')"]}
    ```
  - Returns current URL/title and selector match summary.

- `POST /run`
  - Body:
    ```json
    {
      "token":"YOUR_TOKEN",
      "steps":[
        {"type":"goto","url":"https://github.com/logohehe/logohehe/new/master?profile_readme=1"},
        {"type":"wait_for","selector":"textarea","state":"visible"},
        {"type":"fill","selector":"textarea","text":"# Hello"},
        {"type":"click","selector":"button:has-text('Commit changes...')"}
      ]
    }
    ```

- `POST /stop`
  - Body:
    ```json
    {"token":"YOUR_TOKEN"}
    ```

Supported step types:
- `goto` (`url`)
- `wait_for` (`selector`, optional `state`, `timeout_ms`)
- `click` (`selector`, optional `timeout_ms`)
- `fill` (`selector`, `text`, optional `clear`)
- `type` (`selector`, `text`, optional `delay_ms`)
- `press` (`keys`)
- `sleep` (`seconds`)
- `assert_url_contains` (`text`)
- `assert_exists` (`selector`)
