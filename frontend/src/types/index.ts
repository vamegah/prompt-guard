// Prompt
export interface Prompt {
  tags: never[];
  id: string;
  name: string;
  template: string;
  description?: string;
  version: string;
  metadata: Record<string, any>;
  created_at: string;
  updated_at?: string;
}

export interface PromptCreate {
  name: string;
  template: string;
  description?: string;
  version?: string;
  metadata?: Record<string, any>;
}

export interface PromptUpdate {
  name?: string;
  template?: string;
  description?: string;
  version?: string;
  metadata?: Record<string, any>;
}

// Schema
export interface Schema {
  id: string;
  name: string;
  schema_dict: Record<string, any>;
  description?: string;
  created_at: string;
  updated_at?: string;
}

export interface SchemaCreate {
  name: string;
  schema_dict: Record<string, any>;
  description?: string;
}

export interface SchemaUpdate {
  name?: string;
  schema_dict?: Record<string, any>;
  description?: string;
}

// Test Input
export interface TestInput {
  input_data: Record<string, any>;
  expected_output?: any;
  description?: string;
}

// Test Suite
export interface TestSuite {
  id: string;
  name: string;
  description?: string;
  prompt_ids: string[];
  schema_ids: string[];
  test_inputs: TestInput[];
  created_at: string;
  updated_at?: string;
}

export interface TestSuiteCreate {
  name: string;
  description?: string;
  prompt_ids?: string[];
  schema_ids?: string[];
  test_inputs?: TestInput[];
}

export interface TestSuiteUpdate {
  name?: string;
  description?: string;
  prompt_ids?: string[];
  schema_ids?: string[];
  test_inputs?: TestInput[];
}