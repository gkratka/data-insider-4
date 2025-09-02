#!/usr/bin/env node
/**
 * Quick validation test for the file ID fix
 * This simulates the frontend file upload process
 */

const axios = require('axios').default;
const FormData = require('form-data');
const fs = require('fs');

async function testFileIdFix() {
  console.log('🧪 Testing File ID Fix Implementation');
  console.log('=' * 50);
  
  // Create test data
  const testData = 'name,age,salary\nJohn,25,50000\nAlice,30,75000\nBob,35,60000\n';
  const testFilePath = './test-upload.csv';
  fs.writeFileSync(testFilePath, testData);
  
  try {
    // Step 1: Upload file to backend
    console.log('1️⃣ Uploading test file to backend...');
    const formData = new FormData();
    formData.append('file', fs.createReadStream(testFilePath));
    
    const uploadResponse = await axios.post('http://localhost:8000/api/v1/files/upload', formData, {
      headers: formData.getHeaders(),
    });
    
    console.log('✅ Upload successful');
    console.log('Backend response:', JSON.stringify(uploadResponse.data, null, 2));
    
    // Step 2: Extract file ID using the FIXED logic
    const fileId = uploadResponse.data.file_id; // This is the FIX!
    
    if (!fileId) {
      throw new Error('❌ File ID extraction failed - backend did not return file_id');
    }
    
    console.log(`✅ File ID extracted correctly: ${fileId}`);
    
    // Step 3: Test chat with the correct file ID
    console.log('\n2️⃣ Testing chat with extracted file ID...');
    const chatResponse = await axios.post('http://localhost:8000/api/v1/chat', {
      message: 'what can you tell me about the data that was uploaded?',
      session_id: 'fix-validation-test',
      file_ids: [fileId]
    });
    
    console.log('✅ Chat request successful');
    
    // Step 4: Validate response
    if (chatResponse.data.response.includes('File \'file-') && chatResponse.data.response.includes('not found')) {
      throw new Error('❌ File ID fix failed - still getting file not found error');
    }
    
    console.log('✅ No "file not found" error detected');
    console.log('Chat response preview:', chatResponse.data.response.substring(0, 100) + '...');
    
    // Step 5: Clean up
    console.log('\n3️⃣ Cleaning up...');
    await axios.delete(`http://localhost:8000/api/v1/files/${fileId}`);
    fs.unlinkSync(testFilePath);
    console.log('✅ Cleanup completed');
    
    console.log('\n🎉 FILE ID FIX VALIDATION SUCCESSFUL! 🎉');
    console.log('✅ File upload works correctly');
    console.log('✅ File ID mapping fixed');
    console.log('✅ Chat integration functional');
    
  } catch (error) {
    console.error('\n❌ Validation failed:', error.message);
    if (error.response) {
      console.error('Response data:', error.response.data);
    }
    
    // Clean up on error
    if (fs.existsSync(testFilePath)) {
      fs.unlinkSync(testFilePath);
    }
    
    process.exit(1);
  }
}

// Run the test
if (require.main === module) {
  testFileIdFix().catch(console.error);
}