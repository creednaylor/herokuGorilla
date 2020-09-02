import React from 'react';
import { render } from '@testing-library/react';
import Anchorlink from './Anchorlink';


test('test of Anchorlink', () => {
    const { getByText } = render(<Anchorlink />);
});