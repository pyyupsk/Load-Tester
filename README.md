# Load Testing Tool 🚀

[![Build Python Executable 🚀](https://github.com/pyyupsk/Load-Tester/actions/workflows/build.yml/badge.svg)](https://github.com/pyyupsk/Load-Tester/actions/workflows/build.yml)

Welcome to the **Load Testing Tool** repository! This tool is designed to help you **perform stress tests** on web servers, allowing you to evaluate their capacity to handle varying levels of traffic. While it offers valuable performance metrics, it is essential to use this tool carefully and responsibly.

## 📊 Features

- **Customizable Load Testing**: Easily set the number of requests and concurrency levels to match your testing needs.
- **Proxy Support**: Optionally use multiple proxies to distribute requests and enhance anonymity.
- **Basic Reporting**: View statistics on request success rates, response times, and error summaries to gain insights into server performance.

## 🛠️ Usage

To use this tool, follow these steps:

1. **Download the executable**:

   Visit the [releases page](https://github.com/pyyupsk/Load-Tester/releases) to download the latest version of the Load Testing Tool. Look for the `Load-Tester.exe` file.

2. **Run the load test**:

   Open a command prompt and navigate to the directory where you downloaded the executable. Use the following command format:

   ```bash
   Load-Tester.exe <URL> -n <NUM_REQUESTS> -c <CONCURRENCY> -p <PROXY_FILE>
   ```

### Example Command

```bash
Load-Tester.exe https://example.com -n 1000 -c 100 -p proxies.txt
```

## ⚠️ Important Note

**Use this tool responsibly.** Load testing can significantly affect the performance and availability of web servers. Always ensure you have permission to test the target server, especially if it's a production environment. Running tests without authorization could lead to unintended consequences and potential legal issues.

The authors of this tool cannot be held liable for any damages, downtime, or other adverse effects that may arise from its use. By utilizing this tool, you agree to accept all risks and responsibilities associated with your actions.

## 🤝 Contributing

Contributions are welcome! If you have suggestions for improvements or features, feel free to submit a pull request or open an issue.

## 📝 License

This project is licensed under the [MIT License](LICENSE). See the LICENSE file for more details.

Happy testing! 🎉
