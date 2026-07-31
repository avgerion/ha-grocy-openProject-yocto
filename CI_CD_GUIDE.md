# CI/CD Setup: Building Yocto Images with GitHub Actions

This guide explains how to set up automated Yocto image builds for the Raspberry Pi, what's available on the free tier, and costs.

**For detailed local build instructions, see:** [LOCAL_RUNNER_SETUP.md](LOCAL_RUNNER_SETUP.md)

## GitHub Actions Free Tier

### What You Get for Free

| Resource | Free Tier | Pro/Team |
|----------|-----------|---------|
| **Actions Minutes** | 2,000/month | 10,000/month |
| **Artifact Storage** | 500 MB | 2 GB |
| **Storage Cost** | Free (500 MB limit) | $0.25 per GB/month |
| **Concurrent Jobs** | 20 | 40 |
| **Parallel Jobs** | 20 | 40 |

**Public vs Private Repos:**
- **Public repositories**: Unlimited Actions minutes + 500 MB storage
- **Private repositories**: 2,000 minutes/month + 500 MB storage

### Important: Yocto Build Challenges on Free Tier

**Problem:** Yocto builds are **resource-intensive and time-consuming**

- **Build Time**: 1-3 hours per complete image
- **Image Size**: 1-2 GB (exceeds 500 MB artifact storage)
- **Minutes Used**: 60-180 minutes per build (uses 3-9% of monthly free tier)

**Free Tier Recommendation:**
- ✅ Use Actions for *testing* and *validation* (quick checks)
- ❌ Don't use Actions for complete Yocto builds (hits limits quickly)

## Free Alternatives for Building Yocto Images

### Option 1: Build Locally (RECOMMENDED)

**Best for:** Most users who build infrequently

**For complete step-by-step build instructions, see:** [LOCAL_RUNNER_SETUP.md](LOCAL_RUNNER_SETUP.md)

Quick workflow:

```bash
# Build on your machine (see LOCAL_RUNNER_SETUP.md for detailed setup)
bitbake ha-grocy-openproject-image

# Create release
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# Upload to GitHub Releases
gh release upload v1.0.0 build/tmp/deploy/images/raspberrypi4/ha-grocy-openproject-image-*.wic.bz2
```

**Pros:**
- Free
- Fast (use your own hardware)
- Full control
- No GitHub limits

**Cons:**
- Requires Yocto setup on your machine (see [LOCAL_RUNNER_SETUP.md](LOCAL_RUNNER_SETUP.md))
- Manual upload steps

### Option 2: GitHub Releases (Free Artifact Hosting)

**Best for:** Distributing pre-built images

```bash
# Build locally
bitbake ha-grocy-openproject-image

# Create and upload release
gh release create v1.0.0 \
  -t "Release v1.0.0" \
  -n "Yocto image for Raspberry Pi" \
  build/deploy-images/ha-grocy-openproject-image-*.*.rootfs.rpi-sdimg.xz
```

**Pros:**
- Unlimited artifact storage (GitHub Releases)
- Free bandwidth
- Versioning
- Easy distribution

**Cons:**
- Must build locally
- Manual upload

### Option 3: Self-Hosted Runner

**Best for:** Continuous builds with your own hardware

If you have a Linux machine available:

```yaml
# .github/workflows/build-yocto.yml
name: Build Yocto Image

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Yocto
        run: |
          # Install prerequisites
          sudo apt-get install -y build-essential git python3 wget
          
      - name: Build Image
        run: |
          cd yocto
          # ... build commands
          
      - name: Upload Artifact
        uses: actions/upload-artifact@v3
        with:
          name: yocto-image
          path: build/deploy-images/
          retention-days: 30
```

**Pros:**
- Unlimited build time
- No GitHub limits
- Automated on your hardware
- Free

**Cons:**
- Requires always-on hardware
- You manage infrastructure
- Setup complexity

## Recommended Workflow: Lightweight Actions + Local Builds

### Approach

1. **Local builds** for complete images
2. **GitHub Actions** for validation/testing
3. **GitHub Releases** for distribution

### Workflow Files

#### 1. Linting & Validation (GitHub Actions)

```yaml
# .github/workflows/validate.yml
name: Validate Configuration

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Validate Yocto Config
        run: |
          # Quick validation of bitbake files
          find yocto -name "*.bb" -o -name "*.conf" | wc -l
          echo "Config files found"
          
      - name: Validate Python (Integration)
        run: |
          pip install pylint
          pylint custom_components/home_ops_bridge/ --disable=all --enable=E,F
          
      - name: Test Docker Compose Syntax
        run: |
          cd yocto/layers/meta-ha-grocy-openproject/recipes-containers/ha-grocy-openproject-stack/files
          docker-compose config > /dev/null
```

#### 2. Release Workflow (Publish Pre-Built Image)

```yaml
# .github/workflows/release.yml
name: Create Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Create Release Notes
        run: |
          echo "# Release Notes" > release.txt
          echo "" >> release.txt
          echo "Version: ${{ github.ref }}" >> release.txt
          echo "" >> release.txt
          echo "**Build Instructions:**" >> release.txt
          echo "Follow the steps in BUILD.md to compile the Yocto image." >> release.txt
          echo "" >> release.txt
          echo "**Artifacts:**" >> release.txt
          echo "Download and extract the image file, then flash to SD card." >> release.txt
      
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          body_path: release.txt
          draft: true
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

#### 3. Integration Tests (GitHub Actions)

```yaml
# .github/workflows/integration-tests.yml
name: Integration Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-ha-integration:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Dependencies
        run: |
          pip install homeassistant pytest pytest-asyncio
      
      - name: Run Integration Tests
        run: |
          cd custom_components/home_ops_bridge
          pytest tests/ -v
```

## Building Yocto Images Locally

### Prerequisites

```bash
# Ubuntu/Debian
sudo apt-get install gawk wget git diffstat unzip texinfo gcc build-essential \
  chrpath socat cpio python3 python3-pip python3-pexpect xz-utils debianutils \
  iputils-ping libsdl1.2-dev xterm python3-GitPython git-core gnupg \
  flexbison bison flex libncurses5 libncurses5-dev tinyxml2-dev libudev-dev
```

### Build Steps

```bash
# Clone and setup
mkdir yocto-build && cd yocto-build
git clone https://git.yoctoproject.org/git/poky
git clone https://github.com/avgerion/ha-grocy-openProject-yocto.git

# Setup environment
cd poky
source oe-init-build-env

# Configure build
cp ../ha-grocy-openProject-yocto/yocto/conf/local.conf.sample conf/local.conf
cp ../ha-grocy-openProject-yocto/yocto/conf/bblayers.conf.sample conf/bblayers.conf

# Update layer paths in conf files
# Edit conf/bblayers.conf to point to correct layer paths

# Build
bitbake ha-grocy-openproject-image

# Output
ls -lh tmp/deploy/images/raspberrypi4/ha-grocy-openproject-image-*.rootfs.rpi-sdimg.xz
```

### Build Output

```
deploy/images/raspberrypi4/
├── ha-grocy-openproject-image-raspberrypi4.rootfs.rpi-sdimg.xz
├── ha-grocy-openproject-image-raspberrypi4.rootfs.tar.bz2
└── ...
```

## Distributing Releases

### Using GitHub Releases

```bash
# Tag a release
git tag -a v1.0.0 -m "Release 1.0.0 - Initial public release"
git push origin v1.0.0

# Create release with artifacts
gh release create v1.0.0 \
  -t "v1.0.0: Initial Raspberry Pi Image" \
  -F CHANGELOG.md \
  ./build/deploy-images/ha-grocy-openproject-image-*.xz \
  ./build/deploy-images/ha-grocy-openproject-image-*.sha256sum
```

### Bandwidth (Free)

- GitHub Releases: **Unlimited bandwidth** for downloads
- No egress charges
- Perfect for distributing built images

## Cost Analysis

| Scenario | Cost/Month |
|----------|-----------|
| Local builds only | $0 |
| Actions validation + local builds | $0 (uses free tier) |
| 10 complete Yocto builds on Actions | $40-60 (exceeds limits) |
| Self-hosted runner with artifacts | $0 (your hardware) |

## Recommendations

✅ **For Most Users:**
1. Build locally using Yocto on your development machine
2. Use GitHub Actions for Python/integration testing
3. Publish releases with pre-built images to GitHub Releases
4. Users download from Releases

✅ **For Frequent Builders:**
1. Use self-hosted Actions runner on spare hardware
2. Automate on tag push
3. Publish artifacts to GitHub Releases

❌ **Avoid:**
- Building complete Yocto images on free-tier GitHub Actions
- Storing large artifacts in Actions (exceeds 500 MB)

## See Also

- [GitHub Actions Pricing](https://github.com/pricing)
- [GitHub Releases Documentation](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)
- [Yocto Build System](https://docs.yoctoproject.org/)
- [Self-Hosted Runners](https://docs.github.com/en/actions/hosting-your-own-runners)
