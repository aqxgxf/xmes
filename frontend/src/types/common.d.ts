// Ensure basic types like Company, Unit, MaterialType are defined
// If they are not, or are incomplete, define them or add missing fields.

export interface Company {
  id: number;
  name: string;
  code?: string; // Assuming code is optional or might not be on all nested responses
  // Add other fields if your nested serializer for Company includes them and frontend needs them
}

export interface Unit {
  id: number;
  name: string;
  code?: string;
}

export interface MaterialType {
  id: number;
  name: string;
  code?: string;
}

// ProductCategory for reading (listings, detail views)
export interface ProductCategory {
  id: number;
  code: string;
  display_name: string;
  company: Company | null; // Nested object
  unit: Unit | null;       // Nested object
  material_type: MaterialType | null; // Nested object
  drawing_pdf: string | null; // URL string (this will now hold the full URL or null)
  process_pdf: string | null; // URL string (this will now hold the full URL or null)
  // drawing_pdf_url?: string | null; // REMOVE - covered by drawing_pdf
  // process_pdf_url?: string | null; // REMOVE - covered by process_pdf
  created_at: string;
  // Remove company_name, unit_name, material_type_name if they existed
}

// ProductCategoryForm for creating/editing (stores IDs)
export interface ProductCategoryForm {
  id: number | null;
  code: string;
  display_name: string;
  company: number | null;      // Stores Company ID
  unit: number | null;         // Stores Unit ID
  material_type: number | null; // Stores MaterialType ID
  drawing_pdf?: File | undefined | string; // Can be File for upload, or string (URL from existing data)
  process_pdf?: File | undefined | string; // Can be File for upload, or string (URL from existing data)
  // drawing_pdf_url and process_pdf_url in form are for UI display of current file before new selection
  // these can remain as they are populated by useCategoryForm if needed for the UI
  drawing_pdf_url?: string; 
  process_pdf_url?: string; 
}

// ... other existing type definitions ...

// Example: Ensure your PaginationParams and other related types are still valid.
export interface PaginationParams {
  page?: number;
  page_size?: number;
  search?: string;
  ordering?: string;
} 