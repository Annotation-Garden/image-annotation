/**
 * Version information for Image Annotation Dashboard.
 */

export const VERSION = "0.3.0-beta";
export const VERSION_INFO = {
  major: 0,
  minor: 3,
  patch: 0,
  prerelease: "beta"
} as const;

export function getVersion(): string {
  return VERSION;
}

export function getVersionInfo() {
  return VERSION_INFO;
}
