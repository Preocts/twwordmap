# twwordmap

See `v1/` for the original attempt during #100DaysOfCode 2020

### Authenticating with Twitter API v2 as an application

The authentication client of included in the `twitterapiv2/` library requires your applications consumer credentials to be loaded in the environment variables before an authentication attempt is made. The consumer credentials are your client key and client secret as found in the application dashboard of the Twitter Dev panel.

Create two environmental variables as follows:
```env
TW_CONSUMER_KEY=[client key]
TW_CONSUMER_SECRET=[client secret]
```

A 'TW_BEARER_TOKEN' will be created in the environment on successful authentication. This key should be stored securely and loaded to the environment on subsequent calls. When this token already exists, the request for a bearer token can be skipped.

Additional called to the authentication process **will not** result in a new bearer token if the same consumer credentials are provided. The former bearer token must be invalided to obtain a new one.
