// Keep viewBox (SKILL §6) and the ids the brand guide links to.
export default {
  multipass: true,
  plugins: [
    { name: 'preset-default', params: { overrides: {
        removeViewBox: false,
        cleanupIds: false,
        removeTitle: false,
        removeDesc: { removeAny: false },
    } } },
  ],
};
