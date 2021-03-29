import React, { useState } from 'react';

import PropTypes from 'prop-types';
import styled from 'styled-components';

import AddIcon from '@material-ui/icons/Add';
import Button from '@material-ui/core/Button';
import DelIcon from '@material-ui/icons/Delete';
import TextField from '@material-ui/core/TextField';

function ValueInput(props) {
  const { className, index, onChange, value } = props;

  const handleKeyChange = (e) => {
    onChange(index, e.target.value);
  };

  return (
    <TextField
      className={`${className} inputField`}
      placeholder="Value"
      type="text"
      value={value}
      onChange={handleKeyChange}
    />
  );
}

ValueInput.propTypes = {
  className: PropTypes.string,
  index: PropTypes.number.isRequired,
  onChange: PropTypes.func.isRequired,
  value: PropTypes.string,
};

ValueInput.defaultProps = {
  className: '',
  value: '',
};

const StyledValueInput = styled(ValueInput)`
  &.inputField {
    margin: 10px 10px 10px 0px;
  }
`;

function ValueInputs(props) {
  const { onValueInputsChange } = props;
  const [valueInputs, setValueInputs] = useState([]);

  const onValueChange = (index, value) => {
    const internalValueInputs = [];
    const externalValueInputs = [];

    valueInputs.forEach((valueInput) => {
      if (valueInput.index === index) {
        internalValueInputs.push({ index, value });
        externalValueInputs.push(value);
      } else {
        internalValueInputs.push(valueInput);
        externalValueInputs.push(valueInput.value);
      }
    });

    setValueInputs(internalValueInputs);
    onValueInputsChange(externalValueInputs);
  };

  const onAddClick = () => {
    setValueInputs((previousValueInputs) => [
      ...previousValueInputs,
      { index: Date.now(), value: '' },
    ]);
  };

  const onDeleteValueInput = (index) => {
    const internalValueInputs = [];
    const externalValueInputs = [];
    valueInputs.forEach((valueInput) => {
      if (valueInput.index !== index) {
        internalValueInputs.push(valueInput);
        externalValueInputs.push(valueInput.value);
      }
    });
    setValueInputs(internalValueInputs);
    onValueInputsChange(externalValueInputs);
  };

  return (
    <>
      {valueInputs.map(({ index, value }) => (
        <div key={index}>
          <StyledValueInput
            index={index}
            value={value}
            onChange={onValueChange}
          />
          <Button
            color="default"
            aria-label="del"
            onClick={() => onDeleteValueInput(index)}
          >
            <DelIcon />
          </Button>
        </div>
      ))}
      <Button color="primary" onClick={onAddClick}>
        Add
        <AddIcon />
      </Button>
    </>
  );
}

ValueInputs.propTypes = {
  onValueInputsChange: PropTypes.func.isRequired,
};

export default ValueInputs;
