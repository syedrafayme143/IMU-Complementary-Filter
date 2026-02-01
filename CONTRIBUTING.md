# Contributing to IMU Visualizer

First off, thank you for considering contributing to IMU Visualizer! It's people like you that make this project better for everyone.

## Code of Conduct

This project and everyone participating in it is governed by respect and professionalism. By participating, you are expected to uphold this standard.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (data files, commands used)
- **Describe the behavior you observed** and what you expected
- **Include screenshots** if applicable
- **Note your environment** (OS, Python version, dependency versions)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **List any alternative solutions** you've considered

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. Ensure your code follows the existing style
4. Update documentation as needed
5. Write a clear commit message

## Development Setup

1. Fork and clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/imu-visualizer.git
cd imu-visualizer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a branch:
```bash
git checkout -b feature/your-feature-name
```

## Coding Style

- Follow PEP 8 style guidelines
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and concise
- Comment complex logic

Example:
```python
def process_data(timestamp: float, vector: list) -> tuple:
    """
    Process IMU data and return orientation angles.
    
    Args:
        timestamp (float): Time in seconds
        vector (list): [ax, ay, az, gx, gy, gz]
        
    Returns:
        tuple: (alpha, beta, gamma) angles in radians
    """
    # Your code here
    pass
```

## Testing

Before submitting a pull request:

1. Test with the sample data:
```bash
python src/imu.py data/imudata.txt
```

2. Verify all tabs display correctly
3. Test with different data files if possible
4. Check for any console errors

## Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters
- Reference issues and pull requests after the first line

Good examples:
```
Add Kalman filter option for sensor fusion

Fix angle wrapping bug in gyroscope integration
Closes #123

Update README with new installation instructions
```

## Documentation

- Update README.md if you change functionality
- Add docstrings to new functions/classes
- Update docs/algorithms.md for algorithm changes
- Include code examples where helpful

## Areas for Contribution

Here are some areas where contributions are especially welcome:

### High Priority
- [ ] Unit tests for core algorithms
- [ ] Kalman filter implementation
- [ ] Better error handling
- [ ] Performance optimizations

### Medium Priority
- [ ] 3D visualization
- [ ] Magnetometer support (9-DOF)
- [ ] Export to video/GIF
- [ ] GUI controls for filter parameters

### Low Priority (but still welcome!)
- [ ] Additional plot styles
- [ ] Dark mode theme
- [ ] Configuration file support
- [ ] Multi-language support

## Questions?

Feel free to open an issue with the "question" label if you have any questions about contributing.

## Recognition

Contributors will be recognized in the README. Thank you for your time and effort! 🙏
