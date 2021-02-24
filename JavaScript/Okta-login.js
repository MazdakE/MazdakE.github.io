const oktaSignIn = new OktaSignIn({
    baseUrl: "https://dev-10881290.okta.com",
    clientId: "0oa7o8ki8xMgqrmKv5d6",
    authParams: {
      issuer: "https://dev-10881290.okta.com/oauth2/default",
    },
    redirectUri: "https://mazdake.github.io/",
  });

  oktaSignIn.authClient.token.getUserInfo().then(
    function (user) {
      document.getElementById("messageBox").innerHTML =
        "Hello, " + user.email + "! You are *still* logged in! :)";
      document.getElementById("logout").style.display = "block";
      document.getElementById("navigation-bar").style.display =
        "inline-block";
      document.getElementById("message-box").style.display = "block";
      document.getElementById("article-body").style.display = "flex";
      document.getElementById("scroll-image").style.display = "block";
      document.getElementById("header-currency").style.display = "block";
      document.getElementById("photo-gallery").style.display = "block";
    },
    function (error) {
      oktaSignIn
        .showSignInToGetTokens({
          el: "#okta-login-container",
        })
        .then(function (tokens) {
          oktaSignIn.authClient.tokenManager.setTokens(tokens);
          oktaSignIn.remove();

          const idToken = tokens.idToken;
          document.getElementById("messageBox").innerHTML =
            "Hello, " + idToken.claims.email + "! You just logged in! :)";
          document.getElementById("logout").style.display = "block";
          document.getElementById("navigation-bar").style.display =
            "inline-block";
          document.getElementById("message-box").style.display = "block";
          document.getElementById("article-body").style.display = "flex";
          document.getElementById("scroll-image").style.display = "block";
          document.getElementById("header-currency").style.display =
            "block";
          document.getElementById("photo-gallery").style.display = "block";
        })
        .catch(function (err) {
          console.error(err);
        });
    }
  );

  function logout() {
    oktaSignIn.authClient.signOut();
    location.reload();
  }