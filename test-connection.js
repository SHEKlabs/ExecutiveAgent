// Import your supabase client
import supabase from './supabase/client.js'

async function testConnection() {
  // Attempt to query your "PM - Projects - AR" table
  const { data, error } = await supabase
    .from('PM - Projects - AR')
    .select('*')
    .limit(1)
  
  if (error) {
    console.error('Connection error:', error)
    return
  }
  
  console.log('Connection successful!')
  console.log('Sample data:', data)
}

// Run the test
testConnection()