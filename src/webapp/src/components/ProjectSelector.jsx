import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';

import Input from '@material-ui/core/Input';
import FormControl from '@material-ui/core/FormControl';
import MenuItem from '@material-ui/core/MenuItem';
import Select from '@material-ui/core/Select';

function ProjectSelector(props) {
  const { activeProject, className, projects, onProjectChange } = props;

  const changeProject = (e) => {
    const project = e.target.value;

    // TODO: add project to cookie one level above
    onProjectChange(project);
  };

  const projectElements = projects.map((project) => (
    <MenuItem value={project} key={project.id}>
      {project.name}
    </MenuItem>
  ));

  return (
    //   TODO: add div container?
    <FormControl className={`${className} formControl`}>
      <Select
        className={`${className} select`}
        value={activeProject}
        input={<Input id="select-project" />}
        onChange={changeProject}
      >
        {projectElements}
      </Select>
    </FormControl>
  );
}

ProjectSelector.propTypes = {
  activeProject: PropTypes.instanceOf(Object),
  className: PropTypes.string,
  projects: PropTypes.arrayOf(Object),
  onProjectChange: PropTypes.func.isRequired,
};

ProjectSelector.defaultProps = {
  activeProject: {},
  className: '',
  projects: [],
};

const StyledProjectSelector = styled(ProjectSelector)`
  &.formControl {
    min-width: 120px;
    margin: ${(props) => props.theme.spacing(1)};
    margin-right: 24px;
  }
  &.select {
    color: 'white';
  }
`;

// TODO: connect to Redux!
export default StyledProjectSelector;
