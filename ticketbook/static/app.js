function register()
{
	console.log("hello");
var userPoolId = 'your_user_pool_id';
var clientId = 'your_client_id';

var poolData = { UserPoolId : userPoolId,
  ClientId : clientId
};

var userPool = new AWSCognito.CognitoIdentityServiceProvider.CognitoUserPool(poolData);

  var username = $('#username').val();
  var authenticationData = {
    Username: username,
    Password: $('#password').val()
  };

  var authenticationDetails = new AmazonCognitoIdentity.AuthenticationDetails(authenticationData);

  var userData = {
    Username : username,
    Pool : userPool
  };
  var cognitoUser = new AmazonCognitoIdentity.CognitoUser(userData);

  console.log(cognitoUser);
  cognitoUser.authenticateUser(authenticationDetails, {
    onSuccess: function (result) {
      var accessToken = result.getAccessToken().getJwtToken();
      console.log('Authentication successful', accessToken);
      window.location = './index.html';
    },

    onFailure: function(err) {
      console.log('failed to authenticate');
      console.log(JSON.stringify(err));
      alert('Failed to Log in.\nPlease check your credentials.');
    },
  });

}