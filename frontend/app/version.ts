/**
 * Version information for Image Annotation Dashboard.
 */

export const VERSION = "0.1.5-beta";
export const VERSION_INFO = {
  major: 0,
  minor: 1,
  patch: 5,
  prerelease: "beta"
} as const;

export function getVersion(): string {
  return VERSION;
}

export function getVersionInfo() {
  return VERSION_INFO;
}
