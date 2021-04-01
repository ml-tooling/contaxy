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

function verifyAccess(r, permission) {
  var validInSeconds = 900; // valid for 15 minutes
  // TODO: ngx.fetch allowed in js_set? probably js_content has to be used (see how workspace is handled)
  return ngx
    .fetch(
      `http://localhost:8090/auth/tokens/verify/?permission=${permission}`,
      {
        headers: { Authorization: `Bearer ${apiToken}` },
      }
    )
    .then((res) => {
      // TODO: request was successful, create jwt token
      var generated_session_token = jwt.generate(
        process.env.JWT_SECRET,
        undefined,
        { perms: permission },
        validInSeconds
      );
      r.headersOut[
        "Set-Cookie"
      ] = `ct_session_token=${generated_session_token}; HttpOnly; Path=/; Max-Age=${validInSeconds}`;
      return true;
    })
    .catch((e) => false);
}

function isAuthorized(r) {
  var apiToken = modifyToken(r.variables.cookie_ct_token);
  var sessionToken = modifyToken(r.variables.cookie_ct_session_token);

  if (!apiToken && !sessionToken) return false;
  if (sessionToken) {
    try {
      var jwtPayload = jwt.verify(token, process.env.JWT_SECRET);
    } catch (e) {
      // TODO: make the backend request also here?
      return false;
    }
    r.log(jwtPayload);

    var permission = `projects/${r.variables.project_id}/services/${r.variables.service_id}/access/${r.variables.endpoint}#read`;

    r.log(permission);
    // TODO: check for correct permissions here
    var containsPermission =
      jwtPayload["perms"].indexOf(permission) > -1 ||
      jwtPayload["perms"].indexOf("admin") > -1;
    if (containsPermission) return true;
    if (!containsPermission && apiToken) {
      var res = verifyAccess(r, permission);
      r.log(res);

      return res;
    }
  } else {
    res = verifyAccess(r, permission);
    r.log(res);

    return res;
  }
}

// function checkAuthorization(r) {
//   var apiToken = modifyToken(r.variables.cookie_ct_token);
//   var sessionToken = modifyToken(r.variables.cookie_ct_session_token);

//   if (!apiToken && !sessionToken) return false;
//   if (sessionToken) {
//     try {
//       var jwtPayload = jwt.verify(token, process.env.JWT_SECRET);
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

export default { isAuthorized, token };
