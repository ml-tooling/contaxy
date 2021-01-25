import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import ReactIframe from 'react-iframe';

import GlobalStateContainer from '../app/store';

function Iframe(props) {
  const { className, url, projectSpecific } = props;
  const { activeProject } = GlobalStateContainer.useContainer();
  let iframeUrl = url;
  if (projectSpecific) {
    iframeUrl = `${url}?project=${activeProject.id}`;
  }

  return (
    <ReactIframe
      url={iframeUrl}
      allowFullScreen
      className={`${className} root`}
    />
  );
}

Iframe.propTypes = {
  className: PropTypes.string,
  url: PropTypes.string.isRequired,
  projectSpecific: PropTypes.bool,
};

Iframe.defaultProps = {
  className: '',
  projectSpecific: false,
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
