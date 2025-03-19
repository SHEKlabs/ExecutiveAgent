import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://uhbzldqdbhdyfuxwkqcn.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVoYnpsZHFkYmhkeWZ1eHdrcWNuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0MjE1MDkxNSwiZXhwIjoyMDU3NzI2OTE1fQ.JauAr1A-gaxwNLau9agXY7boGAm01kHJHDTfF-YMDSM'

const supabase = createClient(supabaseUrl, supabaseKey)

export default supabase