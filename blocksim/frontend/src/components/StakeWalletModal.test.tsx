import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import axios from 'axios';
import { StakeWalletModal } from './StakeWalletModal';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('StakeWalletModal', () => {
  test('opens modal and submits stake successfully', async () => {
    mockedAxios.post.mockResolvedValueOnce({ data: { status: 'staked' } });

    const onStake = jest.fn();
    render(<StakeWalletModal onStake={onStake} />);

    // open modal
    fireEvent.click(screen.getByText('Stake to Race'));
    expect(screen.getByPlaceholderText(/Wallet ID/)).toBeInTheDocument();

    fireEvent.change(screen.getByPlaceholderText(/Wallet ID/), { target: { value: '0xabc' } });
    fireEvent.change(screen.getByPlaceholderText(/Amount/), { target: { value: '42' } });

    fireEvent.click(screen.getByText('Confirm'));

    await waitFor(() => expect(onStake).toHaveBeenCalledWith('0xabc', 42));
  });

  test('shows toast on error response', async () => {
    mockedAxios.post.mockResolvedValueOnce({ data: { status: 'failed', reason: 'insufficient' } });
    const onStake = jest.fn();
    const { container } = render(<StakeWalletModal onStake={onStake} />);
    fireEvent.click(screen.getByText('Stake to Race'));
    fireEvent.change(screen.getByPlaceholderText(/Wallet ID/), { target: { value: '0xdef' } });
    fireEvent.click(screen.getByText('Confirm'));
    await waitFor(() => expect(screen.getByText(/Stake failed|Unexpected response/i)).toBeInTheDocument());
    expect(container).toMatchSnapshot();
  });
});
