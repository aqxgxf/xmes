# xMes Production Management System

A comprehensive manufacturing execution system (MES) for production management, built with Django backend and Vue 3 frontend.

## System Architecture

### Backend (Django)

- Django REST framework for API endpoints
- PostgreSQL database
- Token-based authentication
- API structure follows RESTful principles
- Modular apps for different business domains

### Frontend (Vue 3 + TypeScript)

- Modern Vue 3 Composition API with TypeScript
- Pinia for state management
- Vue Router for navigation
- Element Plus for UI components
- Axios for API communication

## Key Features

1. **Production Management**
   - Create and manage production orders
   - Track order status through the production process
   - Manage materials and resources

2. **Sales Management**
   - Customer order management
   - Sales order tracking and fulfillment
   - Order-to-production workflow

3. **Base Data Management**
   - Product catalog management
   - Customer and supplier databases
   - Material inventory

4. **User Management**
   - Role-based access control
   - User authentication and authorization
   - User profiles and preferences

## Code Organization

### Frontend Structure

```
frontend/
├── public/
├── src/
│   ├── api/                # API services
│   │   ├── index.ts        # Axios instance and interceptors
│   │   └── apiUtils.ts     # Common API utility functions
│   ├── assets/             # Static assets (images, fonts)
│   ├── components/         # Reusable Vue components
│   │   ├── common/         # Common UI components
│   │   ├── layout/         # Layout components
│   │   ├── production/     # Production-specific components
│   │   └── sales/          # Sales-specific components
│   ├── router/             # Vue Router configuration
│   ├── stores/             # Pinia stores
│   │   ├── basedata.ts     # Base data store
│   │   ├── production.ts   # Production management store
│   │   ├── sales.ts        # Sales management store
│   │   └── user.ts         # User management store
│   ├── types/              # TypeScript type definitions
│   ├── utils/              # Utility functions
│   │   ├── dateFormatter.ts # Date formatting utilities
│   │   ├── errorHandler.ts  # Error handling utilities
│   │   ├── notification.ts  # Notification utilities
│   │   └── validation.ts    # Form validation utilities
│   ├── views/              # Page components
│   ├── App.vue             # Root component
│   ├── AppLayout.vue       # Main layout
│   └── main.ts             # Application entry point
└── package.json            # Dependencies and scripts
```

### Backend Structure

```
backend/
├── config/                 # Django settings and configuration
├── basedata/               # Base data app (products, customers, etc.)
├── production/             # Production management app
├── sales/                  # Sales management app
├── users/                  # User management app
└── manage.py               # Django management script
```

## Recent Refactoring Improvements

1. **TypeScript Type Enhancements**
   - Added proper type interfaces for all data models
   - Fixed type issues with null vs undefined
   - Added consistent error typing
   - Created centralized common type definitions

2. **Component Refactoring**
   - Created reusable components like OrderForm, DataTable, etc.
   - Improved component props typing
   - Added better error handling in components
   - Enhanced form validation through a dedicated validation utility

3. **Store Improvements**
   - Refactored Pinia stores for better type safety
   - Added common status mappings
   - Improved error handling and loading states
   - Added pagination support
   - Used API utilities for consistent data handling

4. **API Handling**
   - Created centralized API service with interceptors
   - Added utility functions for common API operations
   - Improved error reporting and standardized API response types
   - Implemented consistent error handling across API calls

5. **UI Enhancements**
   - Consistent UI patterns across components
   - Better loading indicators
   - Improved form validation
   - Responsive design improvements
   - Standardized notification system

6. **Frontend Utilities**
   - Created a date formatting utility for consistent date display
   - Implemented a notification utility for consistent user feedback
   - Built a validation utility with common form validation rules
   - Developed an error handling utility with higher-order functions

## Latest Improvements (October 2023)

The most recent refactoring phase focused on:

1. **Backend Improvements**
   - Created Customer and Material proxy models to enhance code organization
   - Added corresponding serializers and viewsets for the new models
   - Enhanced API endpoints to support these new models
   - Fixed import errors and improved error handling

2. **Enhanced Frontend TypeScript Interfaces**
   - Created a centralized common.ts file with shared interfaces
   - Added BaseEntity interface as a foundation for model interfaces
   - Created specific interfaces for Customer, Material, Company and Product
   - Standardized types across the application

3. **Improved Pinia Stores**
   - Refactored Pinia stores to use the new common interfaces
   - Enhanced API response handling and error management
   - Added more robust error handling with custom utility functions
   - Added utility methods for common operations

4. **Extended Validation Utilities**
   - Added company code validation rules
   - Added product code validation rules
   - Created positive number validation
   - Added date validation for future dates
   - Enhanced existing validation rules

5. **Advanced Error Handling**
   - Improved error handler utility with higher-order functions
   - Added withLoading and withErrorHandling wrappers for API calls
   - Enhanced API utilities to standardize error handling across the application
   - Improved error reporting and user feedback

6. **Code Quality Improvements**
   - Better TypeScript typing across the codebase
   - More consistent API response handling
   - Enhanced separation of concerns
   - Improved code reuse through common interfaces and utilities

7. **New Reusable Components**
   - Created FilterForm component for standardized filtering across the application
   - Enhanced date formatting utilities with domain-specific formatters
   - Added specialized API error handling with detailed error messages and codes
   - Improved form validation with domain-specific validation rules

## Previous Improvements (September 2023)

The most recent refactoring phase focused on:

1. **Centralized Error Handling**
   - Created an error handling utility with consistent error formatting
   - Implemented higher-order functions for error handling (withErrorHandling, withLoading)
   - Standardized error messages and logging

2. **Enhanced Form Handling**
   - Improved form components with better validation
   - Added consistent validation rules across forms
   - Enhanced user feedback for form validation errors

3. **Better Date Handling**
   - Implemented a date formatting utility for consistent date display
   - Fixed date conversion issues between backend and frontend
   - Added relative time formatting options

4. **Notification System**
   - Created a centralized notification system for consistent user feedback
   - Standardized success/error messages
   - Added confirmation dialog helpers

5. **Performance Optimization**
   - Improved API data handling to reduce unnecessary requests
   - Added proper pagination support for data tables
   - Implemented data caching strategies in stores

## Development

### Setup

1. Clone the repository
2. Setup backend:
   ```
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

3. Setup frontend:
   ```
   cd frontend
   npm install
   npm run dev
   ```

### Development Practices

- Use TypeScript for all new code
- Follow the Vue 3 Composition API patterns
- Maintain consistent error handling
- Write comprehensive documentation
- Follow existing code style and patterns

## License

Copyright © 2023 xMes Team
