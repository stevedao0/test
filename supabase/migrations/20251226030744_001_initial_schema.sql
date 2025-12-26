/*
  # Initial Database Schema for Contract Management System

  ## Overview
  This migration creates the core tables for managing contracts, annexes, works, and user profiles
  with comprehensive Row Level Security (RLS) policies.

  ## Tables Created
  1. `profiles` - User profiles linked to auth.users
     - `id` (uuid, primary key, references auth.users)
     - `email` (text) - User email
     - `full_name` (text) - Full name
     - `role` (text) - User role: admin, editor, viewer
     - `department` (text) - Department
     - `is_active` (boolean) - Account status
     - `created_at`, `updated_at` (timestamps)

  2. `contracts` - Main contracts table
     - `id` (uuid, primary key)
     - `contract_no` (text, unique) - Contract number like "0001/2025/HDQTGAN-PN/MR"
     - `contract_year` (integer) - Year
     - All business fields: don_vi_ten, don_vi_dia_chi, kenh_ten, etc.
     - `created_by`, `updated_by` (uuid) - Audit references
     - Timestamps

  3. `annexes` - Contract annexes
     - `id` (uuid, primary key)
     - `contract_id` (uuid, references contracts)
     - `annex_no` (text) - Annex number
     - Inherits/overrides business fields from contract
     - Timestamps

  4. `works` - Musical works/items
     - `id` (uuid, primary key)
     - `contract_id` (uuid, references contracts)
     - `annex_id` (uuid, optional, references annexes)
     - Work details: musical_work, author, composer, etc.
     - Timestamps

  5. `audit_logs` - Change tracking
     - `id` (uuid, primary key)
     - `table_name` (text) - Which table was changed
     - `record_id` (uuid) - Which record
     - `action` (text) - INSERT, UPDATE, DELETE
     - `old_data`, `new_data` (jsonb) - Before/after snapshots
     - `user_id` (uuid) - Who made the change
     - `created_at` (timestamp)

  ## Security
  - RLS enabled on all tables
  - Viewers can only SELECT
  - Editors can SELECT, INSERT, UPDATE (no DELETE)
  - Admins have full access
  - All policies require authentication
*/

-- Create enum for user roles
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
    CREATE TYPE user_role AS ENUM ('admin', 'editor', 'viewer');
  END IF;
END $$;

-- Create profiles table
CREATE TABLE IF NOT EXISTS profiles (
  id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email text NOT NULL,
  full_name text,
  role user_role NOT NULL DEFAULT 'viewer',
  department text,
  is_active boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- Create contracts table
CREATE TABLE IF NOT EXISTS contracts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  contract_no text UNIQUE NOT NULL,
  contract_year integer NOT NULL,
  ngay_lap_hop_dong date NOT NULL,
  linh_vuc text NOT NULL DEFAULT 'Sao chép trực tuyến',
  region_code text NOT NULL DEFAULT 'HDQTGAN-PN',
  field_code text NOT NULL DEFAULT 'MR',
  
  don_vi_ten text NOT NULL,
  don_vi_dia_chi text,
  don_vi_dien_thoai text,
  don_vi_nguoi_dai_dien text,
  don_vi_chuc_vu text DEFAULT 'Giám đốc',
  don_vi_mst text,
  don_vi_email text,
  so_cccd text,
  ngay_cap_cccd text,
  
  kenh_ten text,
  kenh_id text,
  nguoi_thuc_hien_email text,
  
  so_tien_chua_gtgt_value bigint,
  so_tien_chua_gtgt_text text,
  thue_percent numeric(5,2),
  thue_gtgt_value bigint,
  thue_gtgt_text text,
  so_tien_value bigint,
  so_tien_text text,
  so_tien_bang_chu text,
  
  docx_path text,
  catalogue_path text,
  
  created_by uuid REFERENCES auth.users(id),
  updated_by uuid REFERENCES auth.users(id),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- Create annexes table
CREATE TABLE IF NOT EXISTS annexes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  contract_id uuid NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
  annex_no text NOT NULL,
  ngay_ky_phu_luc date NOT NULL,
  
  don_vi_ten text,
  don_vi_dia_chi text,
  don_vi_dien_thoai text,
  don_vi_nguoi_dai_dien text,
  don_vi_chuc_vu text,
  don_vi_mst text,
  don_vi_email text,
  so_cccd text,
  ngay_cap_cccd text,
  
  kenh_ten text,
  kenh_id text,
  nguoi_thuc_hien_email text,
  
  so_tien_chua_gtgt_value bigint,
  so_tien_chua_gtgt_text text,
  thue_percent numeric(5,2),
  thue_gtgt_value bigint,
  thue_gtgt_text text,
  so_tien_value bigint,
  so_tien_text text,
  so_tien_bang_chu text,
  
  docx_path text,
  catalogue_path text,
  
  created_by uuid REFERENCES auth.users(id),
  updated_by uuid REFERENCES auth.users(id),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  
  UNIQUE(contract_id, annex_no)
);

-- Create works table
CREATE TABLE IF NOT EXISTS works (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  contract_id uuid NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
  annex_id uuid REFERENCES annexes(id) ON DELETE CASCADE,
  
  stt integer NOT NULL,
  id_link text,
  youtube_url text,
  id_work text,
  musical_work text,
  author text,
  composer text,
  lyricist text,
  time_range text,
  duration text,
  effective_date text,
  expiration_date text,
  usage_type text,
  royalty_rate text,
  note text,
  
  imported_at timestamptz,
  nguoi_thuc_hien text,
  
  created_by uuid REFERENCES auth.users(id),
  created_at timestamptz NOT NULL DEFAULT now()
);

-- Create audit_logs table
CREATE TABLE IF NOT EXISTS audit_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  table_name text NOT NULL,
  record_id uuid NOT NULL,
  action text NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
  old_data jsonb,
  new_data jsonb,
  user_id uuid REFERENCES auth.users(id),
  user_email text,
  ip_address text,
  user_agent text,
  created_at timestamptz NOT NULL DEFAULT now()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_contracts_year ON contracts(contract_year);
CREATE INDEX IF NOT EXISTS idx_contracts_contract_no ON contracts(contract_no);
CREATE INDEX IF NOT EXISTS idx_annexes_contract_id ON annexes(contract_id);
CREATE INDEX IF NOT EXISTS idx_works_contract_id ON works(contract_id);
CREATE INDEX IF NOT EXISTS idx_works_annex_id ON works(annex_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_table_record ON audit_logs(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);

-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE contracts ENABLE ROW LEVEL SECURITY;
ALTER TABLE annexes ENABLE ROW LEVEL SECURITY;
ALTER TABLE works ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Helper function to get current user's role
CREATE OR REPLACE FUNCTION get_user_role()
RETURNS user_role AS $$
  SELECT COALESCE(
    (SELECT role FROM profiles WHERE id = auth.uid()),
    'viewer'::user_role
  );
$$ LANGUAGE sql SECURITY DEFINER STABLE;

-- Helper function to check if user is active
CREATE OR REPLACE FUNCTION is_user_active()
RETURNS boolean AS $$
  SELECT COALESCE(
    (SELECT is_active FROM profiles WHERE id = auth.uid()),
    false
  );
$$ LANGUAGE sql SECURITY DEFINER STABLE;

-- ============================================
-- PROFILES POLICIES
-- ============================================

-- Users can view their own profile
CREATE POLICY "Users can view own profile"
  ON profiles FOR SELECT
  TO authenticated
  USING (auth.uid() = id);

-- Admins can view all profiles
CREATE POLICY "Admins can view all profiles"
  ON profiles FOR SELECT
  TO authenticated
  USING (get_user_role() = 'admin');

-- Admins can update any profile
CREATE POLICY "Admins can update profiles"
  ON profiles FOR UPDATE
  TO authenticated
  USING (get_user_role() = 'admin')
  WITH CHECK (get_user_role() = 'admin');

-- Users can update their own profile (limited fields handled in app)
CREATE POLICY "Users can update own profile"
  ON profiles FOR UPDATE
  TO authenticated
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- Only admins can insert profiles (handled by trigger for new users)
CREATE POLICY "Admins can insert profiles"
  ON profiles FOR INSERT
  TO authenticated
  WITH CHECK (get_user_role() = 'admin');

-- ============================================
-- CONTRACTS POLICIES
-- ============================================

-- All active authenticated users can view contracts
CREATE POLICY "Active users can view contracts"
  ON contracts FOR SELECT
  TO authenticated
  USING (is_user_active());

-- Editors and admins can insert contracts
CREATE POLICY "Editors can insert contracts"
  ON contracts FOR INSERT
  TO authenticated
  WITH CHECK (
    is_user_active() AND 
    get_user_role() IN ('admin', 'editor')
  );

-- Editors and admins can update contracts
CREATE POLICY "Editors can update contracts"
  ON contracts FOR UPDATE
  TO authenticated
  USING (
    is_user_active() AND 
    get_user_role() IN ('admin', 'editor')
  )
  WITH CHECK (
    is_user_active() AND 
    get_user_role() IN ('admin', 'editor')
  );

-- Only admins can delete contracts
CREATE POLICY "Admins can delete contracts"
  ON contracts FOR DELETE
  TO authenticated
  USING (
    is_user_active() AND 
    get_user_role() = 'admin'
  );

-- ============================================
-- ANNEXES POLICIES
-- ============================================

-- All active authenticated users can view annexes
CREATE POLICY "Active users can view annexes"
  ON annexes FOR SELECT
  TO authenticated
  USING (is_user_active());

-- Editors and admins can insert annexes
CREATE POLICY "Editors can insert annexes"
  ON annexes FOR INSERT
  TO authenticated
  WITH CHECK (
    is_user_active() AND 
    get_user_role() IN ('admin', 'editor')
  );

-- Editors and admins can update annexes
CREATE POLICY "Editors can update annexes"
  ON annexes FOR UPDATE
  TO authenticated
  USING (
    is_user_active() AND 
    get_user_role() IN ('admin', 'editor')
  )
  WITH CHECK (
    is_user_active() AND 
    get_user_role() IN ('admin', 'editor')
  );

-- Only admins can delete annexes
CREATE POLICY "Admins can delete annexes"
  ON annexes FOR DELETE
  TO authenticated
  USING (
    is_user_active() AND 
    get_user_role() = 'admin'
  );

-- ============================================
-- WORKS POLICIES
-- ============================================

-- All active authenticated users can view works
CREATE POLICY "Active users can view works"
  ON works FOR SELECT
  TO authenticated
  USING (is_user_active());

-- Editors and admins can insert works
CREATE POLICY "Editors can insert works"
  ON works FOR INSERT
  TO authenticated
  WITH CHECK (
    is_user_active() AND 
    get_user_role() IN ('admin', 'editor')
  );

-- Editors and admins can update works
CREATE POLICY "Editors can update works"
  ON works FOR UPDATE
  TO authenticated
  USING (
    is_user_active() AND 
    get_user_role() IN ('admin', 'editor')
  )
  WITH CHECK (
    is_user_active() AND 
    get_user_role() IN ('admin', 'editor')
  );

-- Only admins can delete works
CREATE POLICY "Admins can delete works"
  ON works FOR DELETE
  TO authenticated
  USING (
    is_user_active() AND 
    get_user_role() = 'admin'
  );

-- ============================================
-- AUDIT_LOGS POLICIES
-- ============================================

-- Admins can view all audit logs
CREATE POLICY "Admins can view audit logs"
  ON audit_logs FOR SELECT
  TO authenticated
  USING (get_user_role() = 'admin');

-- Users can view audit logs for their own actions
CREATE POLICY "Users can view own audit logs"
  ON audit_logs FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

-- System inserts audit logs (via service role or triggers)
CREATE POLICY "System can insert audit logs"
  ON audit_logs FOR INSERT
  TO authenticated
  WITH CHECK (true);

-- ============================================
-- TRIGGERS FOR AUDIT LOGGING
-- ============================================

-- Function to create audit log entry
CREATE OR REPLACE FUNCTION create_audit_log()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    INSERT INTO audit_logs (table_name, record_id, action, new_data, user_id)
    VALUES (TG_TABLE_NAME, NEW.id, 'INSERT', to_jsonb(NEW), auth.uid());
    RETURN NEW;
  ELSIF TG_OP = 'UPDATE' THEN
    INSERT INTO audit_logs (table_name, record_id, action, old_data, new_data, user_id)
    VALUES (TG_TABLE_NAME, NEW.id, 'UPDATE', to_jsonb(OLD), to_jsonb(NEW), auth.uid());
    RETURN NEW;
  ELSIF TG_OP = 'DELETE' THEN
    INSERT INTO audit_logs (table_name, record_id, action, old_data, user_id)
    VALUES (TG_TABLE_NAME, OLD.id, 'DELETE', to_jsonb(OLD), auth.uid());
    RETURN OLD;
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create triggers for audit logging
DROP TRIGGER IF EXISTS contracts_audit ON contracts;
CREATE TRIGGER contracts_audit
  AFTER INSERT OR UPDATE OR DELETE ON contracts
  FOR EACH ROW EXECUTE FUNCTION create_audit_log();

DROP TRIGGER IF EXISTS annexes_audit ON annexes;
CREATE TRIGGER annexes_audit
  AFTER INSERT OR UPDATE OR DELETE ON annexes
  FOR EACH ROW EXECUTE FUNCTION create_audit_log();

DROP TRIGGER IF EXISTS works_audit ON works;
CREATE TRIGGER works_audit
  AFTER INSERT OR UPDATE OR DELETE ON works
  FOR EACH ROW EXECUTE FUNCTION create_audit_log();

-- ============================================
-- TRIGGER FOR AUTO-CREATE PROFILE ON SIGNUP
-- ============================================

CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO profiles (id, email, full_name, role)
  VALUES (
    NEW.id, 
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
    'viewer'::user_role
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();

-- ============================================
-- TRIGGER FOR UPDATED_AT
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS profiles_updated_at ON profiles;
CREATE TRIGGER profiles_updated_at
  BEFORE UPDATE ON profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

DROP TRIGGER IF EXISTS contracts_updated_at ON contracts;
CREATE TRIGGER contracts_updated_at
  BEFORE UPDATE ON contracts
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

DROP TRIGGER IF EXISTS annexes_updated_at ON annexes;
CREATE TRIGGER annexes_updated_at
  BEFORE UPDATE ON annexes
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
