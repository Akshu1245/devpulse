import React from 'react';
import { render, screen } from '@testing-library/react';
import CostIntelligenceDashboard from '../src/components/CostIntelligenceDashboard';

describe('CostIntelligenceDashboard', () => {
  it('renders cost intelligence heading', () => {
    render(<CostIntelligenceDashboard />);
    expect(screen.getByText(/Cost Intelligence/i)).toBeTruthy();
  });

  it('displays provider breakdown section', () => {
    render(<CostIntelligenceDashboard />);
    expect(screen.getByText(/Provider|Breakdown|Cost/i)).toBeTruthy();
  });
});
