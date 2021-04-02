import jwt from "js/jwt.js";

// function getToken(r) {
//   var token = r.headersIn["Authorization"] || r.variables.cookie_ct_token;

//   if (!token) return false;

//   if (token.indexOf("Bearer") > -1) token = token.replace("Bearer", "").trim();

//   return token;
// }

function modifyToken(token) {
  if (!token) return "";
  return token.replace("Bearer", "").trim();
}

function verifyAccess(r, apiToken, permission) {
  var validInSeconds = 900; // valid for 15 minutes
  // TODO: ngx.fetch allowed in js_set? probably js_content has to be used (see how workspace is handled)
  return new Promise((resolve, reject) => {
    ngx
      .fetch(
        `http://localhost:8090/auth/tokens/verify?permission=${encodeURIComponent(
          permission
        )}`,
        {
          method: "POST",
          headers: { Authorization: `Bearer ${apiToken}` },
        }
      )
      .then((res) => {
        // TODO: request was successful, create jwt token
        if (res.status !== 204) {
          r.log("Request failed. Status: " + res.status);
          reject(false);
          return;
        }

        r.log("Fetch request returned: " + res.status);
        r.log(process.env.JWT_TOKEN_SECRET);
        var generated_session_token = jwt.generate(
          process.env.JWT_TOKEN_SECRET,
          undefined,
          { perms: permission },
          validInSeconds
        );
        r.headersOut[
          "Set-Cookie"
        ] = `ct_session_token=${generated_session_token}; HttpOnly; Path=/; Max-Age=${validInSeconds}`;
        resolve(true);
      })
      .catch((e) => {
        r.log("Fetch request failed: " + e);
        reject(false);
      });
  });
}

function isAuthorized(r) {
  var apiToken = modifyToken(r.variables.cookie_ct_token);
  var sessionToken = modifyToken(r.variables.cookie_ct_session_token);
  r.log("In isAuthorized");
  var permission = r.variables.permission;
  r.log("permission: " + permission);
  if (!apiToken && !sessionToken) r.return(403, "No auth cookie set");
  if (sessionToken) {
    try {
      var jwtPayload = jwt.verify(sessionToken, process.env.JWT_TOKEN_SECRET);
    } catch (e) {
      // TODO: make the backend request also here?
      r.return(403, "JWT token not valid");
    }
    r.log(jwtPayload);

    // TODO: check for correct permissions here
    var containsPermission =
      jwtPayload["perms"].indexOf(permission) > -1 ||
      jwtPayload["perms"].indexOf("admin") > -1;
    if (containsPermission) r.internalRedirect("@service");
    if (!containsPermission && apiToken) {
      verifyAccess(r, apiToken, permission)
        .then((res) => {
          r.log("(1) Status: " + res);
          r.internalRedirect("@service");
        })
        .catch((e) => r.return(403, "API Token not valid"));
    }
  } else {
    verifyAccess(r, apiToken, permission)
      .then((res) => {
        r.log("(2) Status: " + res);
        // r.return(200);
        r.internalRedirect("@service");
      })
      .catch((e) => r.return(403, "API Token not valid"));
  }
}

// function checkAuthorization(r) {
//   var apiToken = modifyToken(r.variables.cookie_ct_token);
//   var sessionToken = modifyToken(r.variables.cookie_ct_session_token);

//   if (!apiToken && !sessionToken) return false;
//   if (sessionToken) {
//     try {
//       var jwtPayload = jwt.verify(token, process.env.JWT_TOKEN_SECRET);
//     } catch (e) {
//       // TODO: make the backend request also here?
//       return false;
//     }
//     r.log(jwtPayload);

//     var neededPermission = r.variables.needed_permission;
//     // TODO: check for correct permissions here
//     var containsPermission =
//       jwtPayload["$int_perms"].indexOf(neededPermission) > -1 ||
//       jwtPayload["$int_perms"].indexOf("admin") > -1;
//     if (containsPermission) return true;
//     if (!containsPermission && apiToken) {
//       // TODO: make backend verifyAccess request and verify whether the user has the permission.
//       // TODO: If yes, create a new session token, set it as a cookie and return true.

//       // TODO: ngx.fetch allowed in js_set? probably js_content has to be used (see how workspace is handled)
//       ngx
//         .fetch(
//           `http://localhost:8090/auth/tokens/verify/?permission=projects/${r.variables.project_id}/services/${r.variables.service_id}/access/${r.variables.endpoint}#read`,
//           { headers: { Authorization: `Bearer ${apiToken}` } }
//         )
//         .then((res) => {
//           // TODO: request was successful, create jwt token

//           return true;
//         })
//         .catch((e) => false);
//     }
//   }
// }

export default { isAuthorized };
