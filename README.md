# cm_api
Communicate with crypto exchange [Coinmate.io](https://cointmate.io) through its API

### Configuration
Though there are some cases in which you can get information without using any credentials, setting up a configuration file is highly recommended.

1. To do so, just go to [Cointmate API Key settings](https://coinmate.io/pages/secured/accountAPI.page) to get your apiKey, privateKey and clientID. *Please be advised, that your privateKey is visible for limited time only.* Choose permissions for the APIkey at your own discretion.

        Available permissions are as follows:
            - account info
            - trading enablement
            - withdrawal enablement
1. Include generated credentials in configuration file created using 
   ```python 
   python cm_api -i
   ```

### Currently available options
```
  -h, --help      show this help message and exit
  -i, --initiate  Initiates the script and creates configuration file in
                  cwd for further usage.
  -f, --fees      Checks for current withdrawal fees. (Currently Bitcoin only.)
  -d, --dump      ***WIP*** Dumps current config file including your
                  security credentials. A new config file needs to be
                  configured." Combine with 'cm_api.py -a' to archive
                  current config file.
  -a, --archive   Archives current config file.
  -p, --pairs     Checks for available currency pairs and returns an
                  enumerated list.

```

### Contribution
Feel free to open an issue to discuss further development and features.