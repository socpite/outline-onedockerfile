// jest.config.js at /home/ubuntu/outline
module.exports = {
  transform: {
    "^.+\\.(ts|tsx|js|jsx)$": "esbuild-jest",
  },
  transformIgnorePatterns: ["/node_modules/"],
  moduleFileExtensions: ["ts", "tsx", "js", "jsx", "json"],
  testEnvironment: "node",
};
