/*
  # Create Contract Management Database Schema

  ## Summary
  This migration creates the core database schema for managing contracts and annexes with optimistic locking support for concurrent editing.

  ## New Tables

  ### `contracts` Table
  Stores all contract information including:
  - Contract identification (contract_no, year, linh_vuc)
  - Client information (don_vi_ten, don_vi_dia_chi, contact details)
  - Financial details (amounts, VAT, total)
  - Document paths (docx_path)
  - Version control (version field for optimistic locking)
  - Audit fields (created_at, updated_at, updated_by)

  ### `annexes` Table
  Stores contract annexes (phụ lục):
  - Links to parent contract via contract_id
  - Annex number and date
  - Financial information
  - Version control
  - Audit fields

  ## Security
  - Enable RLS on both tables
  - Policies allow authenticated users full access
  - In production, should be refined to user-specific access

  ## Indexing
  - Unique index on contract_no for fast lookups
  - Index on contract_year for filtering
  - Index on updated_at for sorting
  - Composite index on (contract_no, annex_no) for annexes

  ## Important Notes
  1. **Optimistic Locking**: The `version` column prevents lost updates when multiple users edit simultaneously
  2. **Audit Trail**: All records track who made changes and when
  3. **Cascade Deletion**: Deleting a contract automatically deletes its annexes
*/

-- Create contracts table
CREATE TABLE IF NOT EXISTS contracts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  contract_no text NOT NULL,
  contract_year int NOT NULL,
  ngay_lap_hop_dong date NOT NULL,
  linh_vuc text DEFAULT '',
  region_code text DEFAULT '',
  field_code text DEFAULT '',
  don_vi_ten text DEFAULT '',
  don_vi_dia_chi text DEFAULT '',
  don_vi_dien_thoai text DEFAULT '',
  don_vi_nguoi_dai_dien text DEFAULT '',
  don_vi_chuc_vu text DEFAULT 'Giám đốc',
  don_vi_mst text DEFAULT '',
  don_vi_email text DEFAULT '',
  so_CCCD text DEFAULT '',
  ngay_cap_CCCD text DEFAULT '',
  kenh_ten text DEFAULT '',
  kenh_id text DEFAULT '',
  nguoi_thuc_hien_email text DEFAULT '',
  so_tien_nhuan_but_value bigint DEFAULT NULL,
  so_tien_nhuan_but_text text DEFAULT '',
  so_tien_chua_GTGT_value bigint DEFAULT NULL,
  so_tien_chua_GTGT_text text DEFAULT '',
  thue_percent numeric DEFAULT NULL,
  thue_GTGT_value bigint DEFAULT NULL,
  thue_GTGT_text text DEFAULT '',
  so_tien_value bigint DEFAULT NULL,
  so_tien_text text DEFAULT '',
  so_tien_bang_chu text DEFAULT '',
  docx_path text DEFAULT '',
  version int DEFAULT 1 NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL,
  updated_at timestamptz DEFAULT now() NOT NULL,
  updated_by text DEFAULT 'system',
  CONSTRAINT contracts_contract_no_unique UNIQUE (contract_no)
);

-- Create annexes table
CREATE TABLE IF NOT EXISTS annexes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  contract_id uuid REFERENCES contracts(id) ON DELETE CASCADE,
  contract_no text NOT NULL,
  annex_no text NOT NULL,
  ngay_lap_phu_luc date NOT NULL,
  so_tien_nhuan_but_value bigint DEFAULT NULL,
  so_tien_nhuan_but_text text DEFAULT '',
  docx_path text DEFAULT '',
  version int DEFAULT 1 NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL,
  updated_at timestamptz DEFAULT now() NOT NULL,
  updated_by text DEFAULT 'system',
  CONSTRAINT annexes_contract_annex_unique UNIQUE (contract_no, annex_no)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_contracts_year ON contracts(contract_year);
CREATE INDEX IF NOT EXISTS idx_contracts_updated_at ON contracts(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_contracts_don_vi ON contracts(don_vi_ten);
CREATE INDEX IF NOT EXISTS idx_annexes_contract_id ON annexes(contract_id);
CREATE INDEX IF NOT EXISTS idx_annexes_contract_no ON annexes(contract_no);
CREATE INDEX IF NOT EXISTS idx_annexes_updated_at ON annexes(updated_at DESC);

-- Enable Row Level Security
ALTER TABLE contracts ENABLE ROW LEVEL SECURITY;
ALTER TABLE annexes ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for contracts
CREATE POLICY "Authenticated users can view all contracts"
  ON contracts
  FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Authenticated users can insert contracts"
  ON contracts
  FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Authenticated users can update contracts"
  ON contracts
  FOR UPDATE
  TO authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Authenticated users can delete contracts"
  ON contracts
  FOR DELETE
  TO authenticated
  USING (true);

-- Create RLS policies for annexes
CREATE POLICY "Authenticated users can view all annexes"
  ON annexes
  FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Authenticated users can insert annexes"
  ON annexes
  FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Authenticated users can update annexes"
  ON annexes
  FOR UPDATE
  TO authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Authenticated users can delete annexes"
  ON annexes
  FOR DELETE
  TO authenticated
  USING (true);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for auto-updating timestamps
DROP TRIGGER IF EXISTS update_contracts_updated_at ON contracts;
CREATE TRIGGER update_contracts_updated_at
  BEFORE UPDATE ON contracts
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_annexes_updated_at ON annexes;
CREATE TRIGGER update_annexes_updated_at
  BEFORE UPDATE ON annexes
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Create function for optimistic locking check
CREATE OR REPLACE FUNCTION check_version_conflict()
RETURNS TRIGGER AS $$
BEGIN
  IF OLD.version <> NEW.version - 1 THEN
    RAISE EXCEPTION 'Conflict detected: Record was modified by another user. Please refresh and try again.';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for version conflict detection
DROP TRIGGER IF EXISTS check_contracts_version ON contracts;
CREATE TRIGGER check_contracts_version
  BEFORE UPDATE ON contracts
  FOR EACH ROW
  EXECUTE FUNCTION check_version_conflict();

DROP TRIGGER IF EXISTS check_annexes_version ON annexes;
CREATE TRIGGER check_annexes_version
  BEFORE UPDATE ON annexes
  FOR EACH ROW
  EXECUTE FUNCTION check_version_conflict();