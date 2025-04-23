// screenshot_mcp_wrapper.js
// Node.js MCP wrapper for desktop screenshot that returns imagePath for Cursor chat integration

const { execSync } = require("child_process");
const path = require("path");
const fs = require("fs");

// Example: Use a CLI tool to take a screenshot and save to a known location
const screenshotDir = path.resolve(
  process.env.HOME || process.env.USERPROFILE,
  "Downloads"
);
const screenshotPath = path.join(screenshotDir, `screenshot_${Date.now()}.png`);

try {
  // Replace this command with your preferred screenshot tool
  // Example for macOS: screencapture
  execSync(`screencapture -x "${screenshotPath}"`);

  if (fs.existsSync(screenshotPath)) {
    // Output JSON with imagePath for Cursor
    console.log(JSON.stringify({ imagePath: screenshotPath }));
  } else {
    console.error(
      JSON.stringify({ error: "Screenshot failed, file not found." })
    );
    process.exit(1);
  }
} catch (err) {
  console.error(JSON.stringify({ error: err.message }));
  process.exit(1);
}
