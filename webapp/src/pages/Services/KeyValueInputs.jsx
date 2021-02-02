import React, { useRef, useState } from 'react';
import PropTypes from 'prop-types';

import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import AddIcon from '@material-ui/icons/Add';
import DelIcon from '@material-ui/icons/Delete';

const ENV_NAME_REGEX = new RegExp('^([a-zA-Z_]{1,}[a-zA-Z0-9_]{0,})?$');

const FIELD_KEY = 'Key';
const FIELD_VALUE = 'Value';

function KeyValuePair(props) {
  const [key, setKey] = useState('');
  const [value, setValue] = useState('');
  const [isInvalid, setIsInvalid] = useState(false);

  const { index, onChange } = props;

  const handleKeyChange = (e) => {
    setIsInvalid(!ENV_NAME_REGEX.test(e.target.value));
    setKey(e.target.value);
    onChange(index, key, value);
  };

  const handleValueChange = (e) => {
    setValue(e.target.value);
    onChange(index, key, value);
  };

  return (
    <>
      <TextField
        autoComplete="on"
        placeholder={FIELD_KEY}
        type="text"
        value={key}
        onChange={handleKeyChange}
        error={isInvalid}
        helperText={isInvalid ? 'Key format is not valid' : null}
      />

      <TextField
        autoComplete="on"
        placeholder={FIELD_VALUE}
        type="text"
        value={value}
        onChange={handleValueChange}
      />
    </>
  );
}
KeyValuePair.propTypes = {
  index: PropTypes.number.isRequired,
  onChange: PropTypes.func.isRequired,
};

function KeyValueInputs(props) {
  const [keyValuePairs, setKeyValuePairs] = useState([]);
  const { onKeyValuePairChange } = props;

  // Use a ref here so that the `handleKeyValuePairChange` callback
  // access the right state value and not the one it had when the
  // callback was passed to the child
  const stateRef = useRef();
  stateRef.current = keyValuePairs;

  const handleKeyValuePairChange = (index, key, value) => {
    const newKeyValuePairs = stateRef.current.map((keyValuePair) => {
      if (keyValuePair.index === index) {
        return { index, key, value };
      }
      return keyValuePair;
    });

    setKeyValuePairs(() => [...newKeyValuePairs]);
    onKeyValuePairChange(newKeyValuePairs);
  };

  const handleAddParameterClick = () => {
    setKeyValuePairs((_keyValuePairs) => [
      ..._keyValuePairs,
      { index: Date.now(), key: '', value: '' },
    ]);
  };

  const handleDeleteKeyValueClick = (index) => {
    const newKeyValuePairs = stateRef.current.reduce((result, keyValuePair) => {
      if (keyValuePair.index !== index) {
        result.push(keyValuePair);
      }
      return result;
    }, []);

    setKeyValuePairs(() => [...newKeyValuePairs]);
    onKeyValuePairChange(newKeyValuePairs);
  };

  return (
    <>
      {keyValuePairs.map((keyValuePair) => (
        <div key={keyValuePair.index}>
          <KeyValuePair
            index={keyValuePair.index}
            onChange={handleKeyValuePairChange}
          />
          <Button
            // className={classes.keyValueButton}
            color="default"
            aria-label="del"
            onClick={() => handleDeleteKeyValueClick(keyValuePair.index)}
          >
            <DelIcon />
          </Button>
        </div>
      ))}

      <Button color="primary" onClick={handleAddParameterClick}>
        Add Parameter
        <AddIcon />
      </Button>
    </>
  );
}

KeyValueInputs.propTypes = {
  onKeyValuePairChange: PropTypes.func.isRequired,
};

export default KeyValueInputs;
