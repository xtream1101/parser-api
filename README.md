# Api for parsing things

## Running
`$ pip3 install -r requirements.txt`

`$ gunicorn api:app`

### URL
Parse a full url into its smallest parts

Endpoint: `/parse/url?url={value}`

Example:

Input url: `https://user:pass@test.example.com:8080/foo/bar?arg1=a&arg2=&arg3=hi&arg4&arg3=hello#pg5`

Input url after encoding (this gets passed as the arg): `https%3A%2F%2Fuser%3Apass%40test.example.com%3A8080%2Ffoo%2Fbar%3Farg1%3Da%26arg2%3D%26arg3%3Dhi%26arg4%26arg3%3Dhello%23pg5`

Response:
```
{
  input: "https://user:pass@test.example.com:8080/foo/bar?arg1=a&arg2=&arg3=hi&arg4&arg3=hello#pg5",
  valid_tld: true,
  parts: {
    protocol: "https",
    username: "user",
    password: "pass",
    hash: "#pg5",
    subdomains: [
      "test"
    ],
    rootdomain: "example",
    suffix: "com",
    port: "8080",
    endpoint: "/foo/bar",
    args: {
      arg1: "a",
      arg2: "",
      arg3: [
      "hi",
      "hello"
      ],
      arg4: ""
    }
  }
}
```
* Currently only works with urls that have a valid tld (top level domain). TODO: Get to work with ip's and other hostnames i.e. localhost
