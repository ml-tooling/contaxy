import jwt from "js/jwt.js";

function getToken(r) {
  var token =
    r.headersIn["Authorization"] || r.variables.cookie_lab_access_token;

  if (!token) return false;

  if (token.indexOf("Bearer") > -1) token = token.replace("Bearer", "").trim();

  return token;
}

function isAuthorized(r) {
  var token = getToken(r);
  if (!token) return false;

  var neededPermission = r.variables.needed_permission;

  try {
    var jwtPayload = jwt.verify(token, process.env.JWT_SECRET);
    r.log(jwtPayload);
    var containsPermission =
      jwtPayload["$int_perms"].indexOf(neededPermission) > -1 ||
      jwtPayload["$int_perms"].indexOf("admin") > -1;
    return containsPermission;
  } catch (e) {
    return false;
  }
}

export default { isAuthorized, token };
