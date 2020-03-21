var express = require("express");
var app = express();
var bodyParser = require('body-parser')
global.token_main = ""

app.use(bodyParser.json())
app.listen(3000, () => {
    console.log("Server running on port 3000");
});
app.get("/login/:email/:password", (req, res) => {
    var token_id = Login(req.params.email, req.params.password, logToken);

    function logToken(token_id) {
        console.log("my token " + token_id)
        res.json(token_id);
    }

});


app.post("/signup", (req, res) => {
    sayhello(req.body.name, req.body.email, req.body.phone_number, req.body.password);
    res.json(["Tony", "Lisa", "Michael", "Ginger", "Food"]);

});

app.post("/confirmsignup", (req, res) => {
    console.log("hellow orld");
    Confirm(req.body.otp, req.body.email);
    res.json(["Tony", "Lisa", "Michael", "Ginger", "Food"]);

});

function sayhello(name, email, phone_number, password) {
    console.log("hello");
    const AmazonCognitoIdentity = require('amazon-cognito-identity-js');
    const CognitoUserPool = AmazonCognitoIdentity.CognitoUserPool;
    const AWS = require('aws-sdk');
    const request = require('request');
    const jwkToPem = require('jwk-to-pem');
    const jwt = require('jsonwebtoken');
    global.fetch = require('node-fetch');

    const poolData = {
        UserPoolId: "us-east-1_feVkMHrXA", // Your user pool id here    
        ClientId: "5fl0d45iue53026nou9fq3ppvh" // Your client id here
    };
    const pool_region = 'us-east-1';

    const userPool = new AmazonCognitoIdentity.CognitoUserPool(poolData);

    function RegisterUser() {
        var attributeList = [];
        attributeList.push(new AmazonCognitoIdentity.CognitoUserAttribute({ Name: "name", Value: name }));
        attributeList.push(new AmazonCognitoIdentity.CognitoUserAttribute({ Name: "email", Value: email }));
        attributeList.push(new AmazonCognitoIdentity.CognitoUserAttribute({ Name: "phone_number", Value: phone_number }));

        userPool.signUp(email, password, attributeList, null, function(err, result) {
            if (err) {
                console.log(err);
                return;
            }
            cognitoUser = result.user;
            console.log('user name is ' + cognitoUser.getUsername());
        });
    }
    RegisterUser();
}



function Login(email, password, callback) {
    const AmazonCognitoIdentity = require('amazon-cognito-identity-js');
    const CognitoUserPool = AmazonCognitoIdentity.CognitoUserPool;
    const AWS = require('aws-sdk');
    const request = require('request');
    const jwkToPem = require('jwk-to-pem');
    const jwt = require('jsonwebtoken');
    global.fetch = require('node-fetch');


    const poolData = {
        UserPoolId: "us-east-1_feVkMHrXA", // Your user pool id here    
        ClientId: "5fl0d45iue53026nou9fq3ppvh" // Your client id here
    };
    const pool_region = 'us-east-1';
    const userPool = new AmazonCognitoIdentity.CognitoUserPool(poolData);

    var authenticationDetails = new AmazonCognitoIdentity.AuthenticationDetails({
        Username: email,
        Password: password,
    });

    var userData = {
        Username: email,
        Pool: userPool
    };
    var cognitoUser = new AmazonCognitoIdentity.CognitoUser(userData);

    cognitoUser.authenticateUser(authenticationDetails, {
        onSuccess: function(result) {
            //console.log('access token + ' + result.getAccessToken().getJwtToken());
            //console.log('id token + ' + result.getIdToken().getJwtToken());
            //  console.log('refresh token + ' + result.getRefreshToken().getToken());
            var access_token = result.getAccessToken().getJwtToken()
            var token_id = result.getIdToken().getJwtToken()
            token_main = token_id
            console.log(token_main)
            callback(token_id);
            //return token_id;
        },
        onFailure: function(err) {
            console.log(err);
        },

    });
}



function Confirm(otp, email) {
    console.log(otp, email)
    const AmazonCognitoIdentity = require('amazon-cognito-identity-js');
    const CognitoUserPool = AmazonCognitoIdentity.CognitoUserPool;
    const AWS = require('aws-sdk');
    const request = require('request');
    const jwkToPem = require('jwk-to-pem');
    const jwt = require('jsonwebtoken');
    global.fetch = require('node-fetch');

    const poolData = {
        UserPoolId: "us-east-1_feVkMHrXA", // Your user pool id here    
        ClientId: "5fl0d45iue53026nou9fq3ppvh" // Your client id here
    };
    const pool_region = 'us-east-1';
    const userPool = new AmazonCognitoIdentity.CognitoUserPool(poolData);

    var userData = {
        Username: email,
        Pool: userPool
    };
    var cognitoUser = new AmazonCognitoIdentity.CognitoUser(userData);
    cognitoUser.confirmRegistration(otp, true, function(err, result) {
        if (err) {
            alert(err);
            return;
        }
        alert(result);
    });
}
//Confirm();
//sayhello("vidip");