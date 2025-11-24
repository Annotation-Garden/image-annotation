# Setup Instructions

## Cloning from Source

This repository will be populated by cloning and adapting the existing image annotation tool:

```bash
# Clone the source repository
git clone https://github.com/neuromechanist/image-annotation.git temp-image-annotation

# Copy relevant files to this directory
cp -r temp-image-annotation/* .

# Remove temporary clone
rm -rf temp-image-annotation
```

## Required Modifications

After cloning, the following changes are needed:

### 1. Branding Updates
- [ ] Replace logo with AGI logo (from assets repository)
- [ ] Update color scheme to match AGI theme
- [ ] Ensure logo is positioned top-left

### 2. HED Integration
- [ ] Enhance HED tag support
- [ ] Add HED validation
- [ ] Update documentation for HED workflows

### 3. BIDS Compliance
- [ ] Ensure output follows stimuli-BIDS specifications
- [ ] Add JSON sidecars for annotations
- [ ] Validate against BIDS schema

### 4. Documentation
- [ ] Update README with AGI context
- [ ] Add usage examples
- [ ] Document API if applicable

### 5. Repository Links
- [ ] Link to other AGI repositories
- [ ] Update references from personal to organization
- [ ] Add AGI footer/header

## Testing

After modifications:
- [ ] Verify all functionality works
- [ ] Test HED integration
- [ ] Validate BIDS output
- [ ] Check responsive design with new branding
