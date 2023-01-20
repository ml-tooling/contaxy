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
import TokenType from './TokenType';

/**
 * The AccessToken model module.
 * @module model/AccessToken
 * @version 0.0.23
 */
class AccessToken {
    /**
     * Constructs a new <code>AccessToken</code>.
     * @alias module:model/AccessToken
     * @param token {String} API Token.
     * @param tokenType {module:model/TokenType} The type of the token.
     * @param subject {String} Identifies the principal that is the subject of the token. Usually refers to the user to which the token is issued to.
     * @param scopes {Array.<String>} List of scopes associated with the token.
     */
    constructor(token, tokenType, subject, scopes) { 
        
        AccessToken.initialize(this, token, tokenType, subject, scopes);
    }

    /**
     * Initializes the fields of this object.
     * This method is used by the constructors of any subclasses, in order to implement multiple inheritance (mix-ins).
     * Only for internal use.
     */
    static initialize(obj, token, tokenType, subject, scopes) { 
        obj['token'] = token;
        obj['token_type'] = tokenType;
        obj['subject'] = subject;
        obj['scopes'] = scopes;
    }

    /**
     * Constructs a <code>AccessToken</code> from a plain JavaScript object, optionally creating a new instance.
     * Copies all relevant properties from <code>data</code> to <code>obj</code> if supplied or a new instance if not.
     * @param {Object} data The plain JavaScript object bearing properties of interest.
     * @param {module:model/AccessToken} obj Optional instance to populate.
     * @return {module:model/AccessToken} The populated <code>AccessToken</code> instance.
     */
    static constructFromObject(data, obj) {
        if (data) {
            obj = obj || new AccessToken();

            if (data.hasOwnProperty('token')) {
                obj['token'] = ApiClient.convertToType(data['token'], 'String');
            }
            if (data.hasOwnProperty('token_type')) {
                obj['token_type'] = ApiClient.convertToType(data['token_type'], TokenType);
            }
            if (data.hasOwnProperty('subject')) {
                obj['subject'] = ApiClient.convertToType(data['subject'], 'String');
            }
            if (data.hasOwnProperty('scopes')) {
                obj['scopes'] = ApiClient.convertToType(data['scopes'], ['String']);
            }
            if (data.hasOwnProperty('created_at')) {
                obj['created_at'] = ApiClient.convertToType(data['created_at'], 'Date');
            }
            if (data.hasOwnProperty('expires_at')) {
                obj['expires_at'] = ApiClient.convertToType(data['expires_at'], 'Date');
            }
        }
        return obj;
    }


}

/**
 * API Token.
 * @member {String} token
 */
AccessToken.prototype['token'] = undefined;

/**
 * The type of the token.
 * @member {module:model/TokenType} token_type
 */
AccessToken.prototype['token_type'] = undefined;

/**
 * Identifies the principal that is the subject of the token. Usually refers to the user to which the token is issued to.
 * @member {String} subject
 */
AccessToken.prototype['subject'] = undefined;

/**
 * List of scopes associated with the token.
 * @member {Array.<String>} scopes
 */
AccessToken.prototype['scopes'] = undefined;

/**
 * Creation date of the token.
 * @member {Date} created_at
 */
AccessToken.prototype['created_at'] = undefined;

/**
 * Date at which the token expires and, thereby, gets revoked.
 * @member {Date} expires_at
 */
AccessToken.prototype['expires_at'] = undefined;






export default AccessToken;

