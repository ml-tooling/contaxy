import React from 'react';
import PropTypes from 'prop-types';

import Grid from '@material-ui/core/Grid';
import Widget from './Widget';

function WidgetsGrid(props) {
  const { children, spacing } = props;
  const columnSize = 12 / children.length <= 3 ? 3 : 4;
  const widgets = !Array.isArray(children)
    ? children
    : children.map((child) => (
        <Grid
          key={child.props.name}
          item
          xs={12}
          sm={6}
          md={columnSize}
          lg={columnSize}
        >
          {child}
        </Grid>
      ));

  return (
    <Grid container spacing={spacing}>
      {widgets}
    </Grid>
  );
}

WidgetsGrid.propTypes = {
  children: PropTypes.oneOfType([
    PropTypes.shape({
      type: PropTypes.oneOf([Widget]),
    }),
    PropTypes.arrayOf(
      PropTypes.shape({
        type: PropTypes.oneOf([Widget]),
      })
    ),
  ]).isRequired,
  spacing: PropTypes.number,
};

WidgetsGrid.defaultProps = {
  spacing: 3,
};

export default WidgetsGrid;
