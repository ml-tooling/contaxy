/**
 * Contaxy API
 * Functionality to create and manage projects, services, jobs, and files.
 *
 * The version of the OpenAPI document: 0.0.23
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 *
 */

import ApiClient from '../ApiClient';
import AccessLevel from './AccessLevel';

/**
 * The UserPermission model module.
 * @module model/UserPermission
 * @version 0.0.23
 */
class UserPermission {
    /**
     * Constructs a new <code>UserPermission</code>.
     * @alias module:model/UserPermission
     * @param id {String} Unique ID of the user.
     */
    constructor(id) { 
        
        UserPermission.initialize(this, id);
    }

    /**
     * Initializes the fields of this object.
     * This method is used by the constructors of any subclasses, in order to implement multiple inheritance (mix-ins).
     * Only for internal use.
     */
    static initialize(obj, id) { 
        obj['id'] = id;
    }

    /**
     * Constructs a <code>UserPermission</code> from a plain JavaScript object, optionally creating a new instance.
     * Copies all relevant properties from <code>data</code> to <code>obj</code> if supplied or a new instance if not.
     * @param {Object} data The plain JavaScript object bearing properties of interest.
     * @param {module:model/UserPermission} obj Optional instance to populate.
     * @return {module:model/UserPermission} The populated <code>UserPermission</code> instance.
     */
    static constructFromObject(data, obj) {
        if (data) {
            obj = obj || new UserPermission();

            if (data.hasOwnProperty('username')) {
                obj['username'] = ApiClient.convertToType(data['username'], 'String');
            }
            if (data.hasOwnProperty('email')) {
                obj['email'] = ApiClient.convertToType(data['email'], 'String');
            }
            if (data.hasOwnProperty('disabled')) {
                obj['disabled'] = ApiClient.convertToType(data['disabled'], 'Boolean');
            }
            if (data.hasOwnProperty('id')) {
                obj['id'] = ApiClient.convertToType(data['id'], 'String');
            }
            if (data.hasOwnProperty('permission')) {
                obj['permission'] = ApiClient.convertToType(data['permission'], AccessLevel);
            }
        }
        return obj;
    }


}

/**
 * A unique username on the system.
 * @member {String} username
 */
UserPermission.prototype['username'] = undefined;

/**
 * User email address.
 * @member {String} email
 */
UserPermission.prototype['email'] = undefined;

/**
 * Indicates that user is disabled. Disabling a user will prevent any access to user-accessible resources.
 * @member {Boolean} disabled
 * @default false
 */
UserPermission.prototype['disabled'] = false;

/**
 * Unique ID of the user.
 * @member {String} id
 */
UserPermission.prototype['id'] = undefined;

/**
 * Permissions of the user for the particular project
 * @member {module:model/AccessLevel} permission
 */
UserPermission.prototype['permission'] = undefined;






export default UserPermission;

