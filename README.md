# Load Testing Tool 🚀

[![Build Python Executable 🚀](https://github.com/pyyupsk/Load-Tester/actions/workflows/build.yml/badge.svg?branch=main)](https://github.com/pyyupsk/Load-Tester/actions/workflows/build.yml)

Welcome to the **Load Testing Tool** repository! This powerful tool is designed to **perform stress tests** on web servers, ensuring they can handle high traffic loads while providing valuable performance metrics. Ideal for developers, QA engineers, and anyone who wants to test their web services effectively.

## 📊 Features

- **Customizable Load Testing**: Specify the number of requests and concurrency levels.
- **Proxy Support**: Load test your endpoints using multiple proxies.
- **Detailed Reporting**: Get statistics on request success rates, response times, and error summaries.

## 🛠️ Usage

To use this tool, follow the steps below:

1. **Download the latest executable**:

   You can download the latest version of the Load Testing Tool from the [releases page](https://github.com/pyyupsk/Load-Tester/releases). Choose the `Load-Tester.exe` file.

2. **Run the load test**:

   Open a command prompt and navigate to the directory where you downloaded the executable. Then run the following command:

   ```bash
   Load-Tester.exe <URL> -n <NUM_REQUESTS> -c <CONCURRENCY> -p <PROXY_FILE>
   ```

### Example Command

```bash
Load-Tester.exe https://example.com -n 1000 -c 100 -p proxies.txt
```

## ⚠️ Disclaimer

**Please use this tool responsibly.** Load testing can impact the performance and availability of web servers and services. Always ensure you have permission to test the target server, and avoid performing tests on production environments without prior consent from the server owner. The authors of this tool are not liable for any damages, downtime, or adverse effects resulting from the use of this software. By using this tool, you acknowledge that you understand the risks involved and agree to use it at your own discretion.

## 🤝 Contributing

We welcome contributions to enhance this project!

## 📝 License

This project is licensed under the [MIT License](LICENSE). See the LICENSE file for more details.

Happy testing! 🎉
