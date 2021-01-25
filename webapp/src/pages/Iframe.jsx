import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import ReactIframe from 'react-iframe';

function Iframe(props) {
  const { className, url } = props;
  return (
    <ReactIframe url={url} allowFullScreen className={`${className} root`} />
  );
}

Iframe.propTypes = {
  className: PropTypes.string,
  url: PropTypes.string.isRequired,
};

Iframe.defaultProps = {
  className: '',
};

const StyledIframeComponent = styled(Iframe)`
  &.root {
    position: absolute;
    width: 100%;
    height: 100%;
    border: none;
  }
`;

export default StyledIframeComponent;
