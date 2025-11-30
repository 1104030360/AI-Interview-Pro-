/**
 * Utility function for merging class names
 * Combines multiple class name arguments into a single string
 */
export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ');
}
