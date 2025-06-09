import { render, screen, waitFor } from "@testing-library/react";
import Dashboard from "../pages/Dashboard";
import React from "react";

// PUBLIC_INTERFACE
test("renders dashboard header and loading initially", async () => {
  render(<Dashboard />);
  expect(screen.getByText(/Welcome to CodeQuest Arena/i)).toBeInTheDocument();
  // Should show loading skeleton/glass by default
  expect(screen.getByText(/Loading live data/i)).toBeInTheDocument();
});
