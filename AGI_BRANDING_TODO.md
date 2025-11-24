# AGI Branding Customization Checklist

This document tracks the required changes to adapt the image-annotation tool for the Annotation Garden Initiative.

## High Priority - Visual Branding

### Logo Integration
- [ ] Add AGI logo to frontend (from ../assets/AGI-square.svg)
- [ ] Position logo top-left in header/navbar
- [ ] Update favicon to AGI logo
- [ ] Replace any existing branding elements

### Color Theme
- [ ] Extract color palette from AGI logo
- [ ] Update CSS/styling to use AGI colors
- [ ] Update frontend theme configuration
- [ ] Ensure consistent colors across all pages

### Typography and Layout
- [ ] Ensure consistent with annotation.garden website
- [ ] Update any custom fonts to match AGI style
- [ ] Verify responsive design with new branding

## High Priority - Content Updates

### Links and References
- [ ] Update repository URLs from neuromechanist to Annotation-Garden
- [ ] Update live dashboard link when deployed
- [ ] Add links to other AGI repositories
- [ ] Update CONTRIBUTING.md links to AGI management repo

### Documentation
- [ ] Replace README.md with README_AGI.md content
- [ ] Add AGI context to all documentation
- [ ] Update installation instructions with AGI organization
- [ ] Add link to AGI white paper

### Footer/Header
- [ ] Add AGI initiative tagline
- [ ] Include link to annotation.garden
- [ ] Add copyright/attribution for AGI

## Medium Priority - HED Integration

### HED Tag Support
- [ ] Review current HED implementation
- [ ] Enhance HED tag suggestions
- [ ] Add HED validation using hedtools
- [ ] Document HED workflow in user guide

### HED Export
- [ ] Ensure annotations export with HED tags
- [ ] Validate against HED schema
- [ ] Add HED JSON sidecars
- [ ] Test with hedtools validation

## Medium Priority - BIDS Compliance

### Output Format
- [ ] Verify events.tsv format follows stimuli-BIDS
- [ ] Add JSON sidecars for annotation schema
- [ ] Test BIDS validation
- [ ] Document BIDS compliance in README

### File Structure
- [ ] Align directory structure with BIDS conventions
- [ ] Add dataset_description.json
- [ ] Include BIDS-compliant metadata

## Low Priority - Feature Enhancements

### GitHub Integration
- [ ] Add GitHub authentication for collaborative annotations
- [ ] Enable annotation versioning
- [ ] Add PR workflow for annotation contributions

### Multi-user Support
- [ ] Track annotator identity
- [ ] Enable annotation comparison across users
- [ ] Add inter-annotator agreement metrics

### API Integration
- [ ] Create API for AGI platform integration
- [ ] Enable cross-repository annotation queries
- [ ] Add webhook support for updates

## Testing Requirements

Before completion, verify:
- [ ] All AGI branding elements are present
- [ ] Logo displays correctly on all pages
- [ ] Color theme is consistent throughout
- [ ] Links point to AGI organization
- [ ] HED validation works
- [ ] BIDS output is compliant
- [ ] Documentation is accurate and complete

## Deployment

- [ ] Update GitHub repository settings
- [ ] Configure GitHub Pages for AGI organization
- [ ] Update domain configuration if applicable
- [ ] Test deployed version

## Notes

- Preserve original functionality while adding AGI context
- Maintain compatibility with existing annotation workflows
- Document all changes for future contributors
- Keep original license (CC-BY-NC-SA 4.0) with proper attribution
