# Frontend Components Module

## Overview

The components module contains reusable React components that form the building blocks of the Equity Valuation System user interface. These components follow modern React patterns with TypeScript, implement consistent design systems, and provide cross-cutting functionality like authentication, theming, and data visualization.

## Role and Responsibilities

### Primary Functions
- **UI Component Library**: Reusable interface components with consistent styling
- **Authentication Guards**: Route protection and user session management
- **Data Visualization**: Interactive charts and graphs for financial data
- **Layout Management**: Responsive layout components and navigation
- **Theme Management**: Dark/light mode toggle and consistent styling

### Key Components
- `Layout`: Main application layout with navigation and header
- `ProtectedRoute`: Authentication guard for secure routes
- `ThemeToggle`: User interface for switching between light/dark themes  
- `PriceChart`: Interactive financial data visualization component

## Architecture

### Component Design Patterns
- **Composition over Inheritance**: Components built using composition patterns
- **Props Interface**: TypeScript interfaces for type-safe prop passing
- **Controlled Components**: State management through props and callbacks
- **Presentational/Container**: Separation of UI and business logic

### State Management
- **React Context**: Global state for authentication and theming
- **Local State**: Component-level state using React hooks
- **Props Drilling**: Explicit prop passing for component communication
- **Event Handling**: Callback props for parent-child communication

### Styling Architecture
- **Tailwind CSS**: Utility-first CSS framework for consistent styling
- **CSS Modules**: Scoped styling for component-specific styles
- **Theme Variables**: CSS custom properties for theme customization
- **Responsive Design**: Mobile-first responsive breakpoints

## Key Dependencies

### Core React Libraries
- `react`: Core React library (v18.2.0)
- `react-dom`: React DOM rendering
- `react-router-dom`: Client-side routing and navigation
- `@types/react`: TypeScript type definitions for React

### UI and Visualization
- `chart.js`: Powerful charting library for financial data visualization
- `react-chartjs-2`: React wrapper for Chart.js integration
- `tailwindcss`: Utility-first CSS framework
- `date-fns`: Date utility library for formatting and calculations

### Development Tools
- `typescript`: Static type checking
- `@testing-library/react`: Testing utilities for React components
- `@testing-library/jest-dom`: Additional Jest matchers for DOM testing

## Setup Instructions

### Environment Configuration
```bash
# Install dependencies
npm install

# Set up environment variables
echo "REACT_APP_API_URL=http://localhost:8000" > .env.local
echo "REACT_APP_ENVIRONMENT=development" >> .env.local
```

### Theme Configuration
```typescript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          900: '#1e3a8a',
        },
        secondary: {
          50: '#f8fafc',
          500: '#64748b',
          900: '#0f172a',
        }
      }
    }
  }
}
```

## Usage Guide

### Layout Component
The main application layout component providing consistent structure:

```tsx
import { Layout } from '../components/Layout';

function App() {
  return (
    <Layout>
      <div className="p-6">
        <h1>Dashboard Content</h1>
      </div>
    </Layout>
  );
}
```

**Props Interface:**
```typescript
interface LayoutProps {
  children: React.ReactNode;
  title?: string;
  showSidebar?: boolean;
}
```

### ProtectedRoute Component
Authentication guard for securing routes:

```tsx
import { ProtectedRoute } from '../components/ProtectedRoute';
import { Dashboard } from '../pages/Dashboard';

function App() {
  return (
    <Routes>
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <Dashboard />
        </ProtectedRoute>
      } />
    </Routes>
  );
}
```

**Props Interface:**
```typescript
interface ProtectedRouteProps {
  children: React.ReactNode;
  fallback?: React.ComponentType;
  requiredRole?: string;
}
```

### ThemeToggle Component
User interface for theme switching:

```tsx
import { ThemeToggle } from '../components/ThemeToggle';

function Header() {
  return (
    <header className="flex justify-between items-center">
      <h1>Equity Valuator</h1>
      <ThemeToggle />
    </header>
  );
}
```

**Props Interface:**
```typescript
interface ThemeToggleProps {
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}
```

### PriceChart Component
Interactive financial data visualization:

```tsx
import { PriceChart } from '../components/PriceChart';

function CompanyView({ companyId }: { companyId: string }) {
  return (
    <div>
      <PriceChart 
        companyId={companyId}
        chartType="line"
        dateRange="1y"
        showVolume={true}
      />
    </div>
  );
}
```

**Props Interface:**
```typescript
interface PriceChartProps {
  companyId: string;
  chartType?: 'line' | 'candlestick' | 'bar';
  dateRange?: '1d' | '1w' | '1m' | '3m' | '6m' | '1y' | '2y' | '5y';
  showVolume?: boolean;
  height?: number;
  onDataPointClick?: (dataPoint: PriceDataPoint) => void;
}
```

## Testing Instructions

### Unit Tests
```bash
# Run component tests
npm test

# Run specific component test
npm test -- --testNamePattern="Layout"

# Run tests with coverage
npm test -- --coverage
```

### Component Testing Examples
```typescript
// Layout.test.tsx
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../contexts/AuthContext';
import { Layout } from './Layout';

test('renders layout with navigation', () => {
  render(
    <BrowserRouter>
      <AuthProvider>
        <Layout>
          <div>Test Content</div>
        </Layout>
      </AuthProvider>
    </BrowserRouter>
  );

  expect(screen.getByText('Test Content')).toBeInTheDocument();
  expect(screen.getByRole('navigation')).toBeInTheDocument();
});
```

### Integration Tests
```bash
# Test component interactions
npm test -- --testPathPattern="integration"

# Test with real API calls (requires backend)
npm run test:integration
```

### Visual Testing
```bash
# Run Storybook for visual component testing
npm run storybook

# Build Storybook for production
npm run build-storybook
```

## Component Specifications

### Layout Component

**Purpose:** Provides consistent application layout with navigation, header, and content areas.

**Features:**
- Responsive sidebar navigation
- User authentication display
- Breadcrumb navigation
- Mobile-optimized hamburger menu
- Theme-aware styling

**State Management:**
- Uses AuthContext for user state
- Uses ThemeContext for theme state
- Local state for mobile menu toggle

### ProtectedRoute Component

**Purpose:** Implements route-level authentication and authorization.

**Features:**  
- JWT token validation
- Automatic redirect to login
- Role-based access control
- Loading state handling
- Error boundary integration

**Security Considerations:**
- Token expiration handling
- Secure token storage
- CSRF protection
- XSS prevention

### ThemeToggle Component

**Purpose:** Provides user interface for switching between light and dark themes.

**Features:**
- Smooth theme transitions
- System theme detection
- Persistent theme preference
- Accessibility compliance (WCAG 2.1)
- Icon-based toggle interface

**Accessibility:**
- ARIA labels for screen readers
- Keyboard navigation support
- High contrast mode compatibility
- Reduced motion preferences

### PriceChart Component

**Purpose:** Interactive visualization of financial price and volume data.

**Features:**
- Multiple chart types (line, candlestick, bar)
- Configurable date ranges
- Volume overlay display
- Interactive tooltips
- Responsive design
- Real-time data updates

**Performance:**
- Virtual scrolling for large datasets
- Efficient re-rendering
- Memory leak prevention
- Debounced resize handling

## Styling Guidelines

### Tailwind CSS Classes
```typescript
// Common utility patterns
const buttonStyles = "px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2";

const cardStyles = "bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700";

const inputStyles = "w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white";
```

### Theme Variables
```css
:root {
  /* Light theme */
  --color-primary: #3b82f6;
  --color-background: #ffffff;
  --color-text: #1f2937;
  --color-border: #d1d5db;
}

[data-theme='dark'] {
  /* Dark theme */
  --color-primary: #60a5fa;
  --color-background: #1f2937;
  --color-text: #f9fafb;
  --color-border: #374151;
}
```

### Responsive Breakpoints
```typescript
// Tailwind breakpoint system
const breakpoints = {
  'sm': '640px',   // Mobile landscape
  'md': '768px',   // Tablet
  'lg': '1024px',  // Desktop
  'xl': '1280px',  // Large desktop
  '2xl': '1536px'  // Extra large desktop
};
```

## Performance Considerations

### Component Optimization
- **React.memo**: Memoization for expensive render operations
- **useCallback**: Memoized event handlers to prevent unnecessary re-renders
- **useMemo**: Memoized calculations and derived state
- **Code Splitting**: Dynamic imports for large components

### Bundle Optimization
- **Tree Shaking**: Eliminate unused code from final bundle
- **Code Splitting**: Split components into separate bundles
- **Lazy Loading**: Load components only when needed
- **Asset Optimization**: Optimize images and fonts

### Runtime Performance
- **Virtual Scrolling**: For large data lists
- **Debounced Inputs**: Reduce API calls from user input
- **Event Delegation**: Efficient event handling for lists
- **Memory Management**: Proper cleanup of event listeners and subscriptions

## Accessibility Standards

### WCAG 2.1 Compliance
- **Level AA** compliance for all components
- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Reader Support**: ARIA labels and semantic HTML
- **Color Contrast**: Minimum 4.5:1 contrast ratio
- **Focus Management**: Visible focus indicators

### Implementation Examples
```typescript
// Accessible button component
function Button({ children, onClick, disabled, ariaLabel }: ButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      aria-label={ariaLabel}
      className="focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
    >
      {children}
    </button>
  );
}

// Accessible form input
function Input({ label, value, onChange, required }: InputProps) {
  const inputId = useId();
  
  return (
    <div>
      <label htmlFor={inputId} className="block text-sm font-medium">
        {label} {required && <span aria-label="required">*</span>}
      </label>
      <input
        id={inputId}
        value={value}
        onChange={onChange}
        required={required}
        aria-describedby={required ? `${inputId}-required` : undefined}
      />
    </div>
  );
}
```