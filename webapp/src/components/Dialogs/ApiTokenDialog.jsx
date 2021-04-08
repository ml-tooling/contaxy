import React, { useRef, useState } from 'react';

import PropTypes from 'prop-types';
import styled from 'styled-components';

import Button from '@material-ui/core/Button';
import CopyIcon from '@material-ui/icons/Assignment';
import DeleteIcon from '@material-ui/icons/Delete';
import DetailsIcon from '@material-ui/icons/Details';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';
import Divider from '@material-ui/core/Divider';
import Popover from '@material-ui/core/Popover';
// import Tab from '@material-ui/core/Tab';
// import Tabs from '@material-ui/core/Tabs';
import TextField from '@material-ui/core/TextField';
import Tooltip from '@material-ui/core/Tooltip';
import Typography from '@material-ui/core/Typography';

import ReactJson from 'react-json-view';

import { authApi } from '../../services/contaxy-api';
import ApiToken from '../../services/contaxy-client/model/ApiToken';
import ValueInputs from './ValueInputs';
import setClipboardText from '../../utils/clipboard';
import showStandardSnackbar from '../../app/showStandardSnackbar';

function ApiTokenDialog({ className, creationScope, tokens, onClose }) {
  const textFieldRef = useRef();
  const [selectedPanel] = useState(0);
  const [tokenDetails, setTokenDetails] = useState({});
  const [scopes, setScopes] = useState([]);
  const [_tokens, setTokens] = useState(tokens);

  const handleCopyClick = () => {
    setClipboardText(null, textFieldRef.current);
  };

  const onGenerateToken = async () => {
    try {
      const token = await authApi.createToken({
        scopes,
        tokenType: 'api-token',
      });
      // TODO: the returned 'token' is a string and not an AccessToken yet
      setTokens([..._tokens, { token }]);
    } catch (e) {
      showStandardSnackbar(`Could not create API token. Reason: ${e.message}`);
    }
  };

  const onShowDetails = (htmlElement, token) => {
    setTokenDetails({ element: htmlElement, token });
  };

  const onDeleteToken = async (token) => {
    try {
      await authApi.revokeToken(token.token);
      setTokens(_tokens.filter((t) => t.token !== token.token));
      showStandardSnackbar(`Revoked token '${token.token}'.`);
    } catch (e) {
      showStandardSnackbar(
        `Could not revoke token '${token.token}'. Reason: ${e.message}`
      );
    }
  };

  const popoverElement = tokenDetails.token && (
    <Popover
      open
      anchorEl={tokenDetails.element}
      onClose={() => setTokenDetails({})}
      anchorOrigin={{
        vertical: 'bottom',
        horizontal: 'left',
      }}
      transformOrigin={{
        vertical: 'top',
        horizontal: 'left',
      }}
    >
      <div className={`${className} popovercontent`}>
        <ReactJson src={tokenDetails.token} />
      </div>
    </Popover>
  );

  const tokenElements = _tokens.map((token) => {
    return (
      <div key={token.token} className={`${className} displaytoken`}>
        <Typography
          className={`${className} displaytoken-token`}
          ref={textFieldRef}
        >
          {token.token}
        </Typography>
        <Tooltip title="Copy" aria-label="copy">
          <Button
            className={`${className} displaytoken-button`}
            onClick={() => handleCopyClick()}
          >
            <CopyIcon fontSize="small" />
          </Button>
        </Tooltip>
        <Tooltip title="Details" aria-label="details">
          <Button
            className={`${className} displaytoken-button`}
            onClick={(event) => onShowDetails(event.currentTarget, token)}
          >
            <DetailsIcon fontSize="small" />
          </Button>
        </Tooltip>
        <Tooltip title="Delete" aria-label="delete">
          <Button
            className={`${className} displaytoken-button`}
            onClick={() => onDeleteToken(token)}
          >
            <DeleteIcon fontSize="small" />
          </Button>
        </Tooltip>
      </div>
    );
  });

  const displayTokensPanel = (
    <>
      <Typography variant="subtitle1">Existing Tokens</Typography>
      {tokenElements && tokenElements.length > 0
        ? tokenElements
        : 'No API tokens exist'}
    </>
  );
  const createTokenPanel = (
    <div>
      <Typography variant="subtitle1">Token Creation</Typography>
      <Typography variant="subtitle2">Scopes</Typography>
      <ValueInputs
        initialValues={[creationScope]}
        inputComponent={(props) => {
          /* eslint-disable react/prop-types */

          const handleInputChange = (e) => {
            props.onChange(props.index, {
              input: e.target.value,
              level: props.value.level,
            });
          };

          const handleLevelChange = (e) => {
            props.onChange(props.index, {
              input: props.value.input,
              level: e.target.value,
            });
          };

          return (
            <div>
              <TextField
                className={`${className} inputField`}
                placeholder={props.placeholder}
                type="text"
                value={props.value.input}
                onChange={handleInputChange}
                fullWidth
              />
              <TextField
                type="text"
                value={props.value.level}
                onChange={handleLevelChange}
              />
            </div>
          );
          /* eslint-enable react/prop-types */
        }}
        onValueInputsChange={setScopes}
        placeholder="Scope"
      />
      <div className={`${className} createtoken`}>
        <Button
          color="secondary"
          aria-label="create-token"
          onClick={() => onGenerateToken()}
        >
          Create API Token
        </Button>
      </div>
    </div>
  );

  return (
    <Dialog classes={{ paper: `${className} dialog` }} open>
      <DialogTitle>API TOKENS</DialogTitle>
      <DialogContent>
        {/* <Tabs
          value={selectedPanel}
          onChange={(event, index) => setSelectedPanel(index)}
          aria-label="token tabs"
        >
          <Tab label="Display Tokens" id="token-tab-0" />
          <Tab label="Create Token" id="token-tab-1" />
        </Tabs> */}
        {selectedPanel === 0 && displayTokensPanel}
        <Divider className={`${className} divider`} />
        {selectedPanel === 0 && createTokenPanel}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="primary">
          OK
        </Button>
      </DialogActions>
      {popoverElement}
    </Dialog>
  );
}

ApiTokenDialog.propTypes = {
  className: PropTypes.string,
  creationScope: PropTypes.string,
  tokens: PropTypes.arrayOf(PropTypes.instanceOf(ApiToken)),
  onClose: PropTypes.func.isRequired,
};

ApiTokenDialog.defaultProps = {
  className: '',
  creationScope: '',
  tokens: [],
};

const StyledApiTokenDialog = styled(ApiTokenDialog)`
  &.dialog {
    min-width: 25%;
  }

  &.createtoken {
    display: flex;
    justify-content: flex-end;
  }

  &.displaytoken {
    display: flex;
    align-items: center;
  }

  &.displaytoken-token {
    width: 80%;
    margin-right: 8px;
  }

  &.displaytoken-button {
    min-width: initial;
  }

  &.divider {
    margin-top: 16px;
    margin-bottom: 16px;
  }

  &.popovercontent {
    margin: 8px;
  }
`;

export default StyledApiTokenDialog;
