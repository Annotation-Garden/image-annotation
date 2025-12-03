/**
 * Version information for Image Annotation Dashboard.
 */

export const VERSION = "0.2.0-beta";
export const VERSION_INFO = {
  major: 0,
  minor: 2,
  patch: 0,
  prerelease: "beta"
} as const;

export function getVersion(): string {
  return VERSION;
}

export function getVersionInfo() {
  return VERSION_INFO;
}
