# Distributed E-Commerce Transaction Analytics Using Hadoop HDFS and MapReduce

A Big Data Analytics project that analyzes the UCI Online Retail transaction dataset using Apache Hadoop, HDFS, Hadoop MapReduce, Python, Docker, Pandas, and Matplotlib.

## 1. Project Overview

E-commerce businesses generate large amounts of transaction data. Analyzing this data helps identify high-revenue countries, popular products, monthly sales trends, transaction patterns, and potential cancellations.

This project demonstrates two complementary components:

1. **Distributed processing:** Hadoop HDFS stores the dataset, while Hadoop MapReduce processes transaction records and aggregates line-item revenue by country.
2. **Exploratory data analysis:** A separate Python analytics script uses Pandas and Matplotlib to calculate business metrics and generate 13 visualizations.

The Hadoop environment runs in Docker containers with one master node and two worker nodes.

## 2. Project Objectives

- Configure a Hadoop cluster consisting of one master and two workers.
- Store and verify transaction data in HDFS.
- Demonstrate distributed data processing using Hadoop MapReduce.
- Implement a Python mapper and reducer using Hadoop Streaming.
- Calculate country-level revenue totals.
- Perform additional exploratory analysis using Pandas.
- Generate visualizations to communicate business insights.
- Verify cluster health, DataNode availability, HDFS file integrity, and job completion.
- Maintain project code, analytical outputs, and documentation in GitHub.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Apache Hadoop 3.3.6 | Distributed data-processing framework |
| HDFS | Distributed file storage and block replication |
| Hadoop MapReduce | Parallel processing and aggregation |
| Hadoop Streaming | Executes Python mapper and reducer programs |
| YARN | Cluster resource management and job scheduling |
| Docker | Runs the master and worker containers |
| Python 3 | Mapper, reducer, and analytics implementation |
| Pandas | Data cleaning, grouping, aggregation, and analysis |
| Matplotlib | Generates charts and visualizations |
| Git and GitHub | Version control and project hosting |

## 4. Dataset

**Dataset:** UCI Online Retail

Source: https://archive.ics.uci.edu/dataset/352/online+retail

The dataset contains historical transactions from a UK-based online retail business between December 2010 and December 2011.

### Dataset attributes

| Column | Description |
|---|---|
| `InvoiceNo` | Invoice or transaction identifier |
| `StockCode` | Product identifier |
| `Description` | Product description |
| `Quantity` | Number of units purchased or returned |
| `InvoiceDate` | Date and time of the transaction |
| `UnitPrice` | Recorded unit price |
| `CustomerID` | Customer identifier |
| `Country` | Customer's country |

### Dataset statistics

- Raw records: 541,909
- Dataset size: approximately 48.6 MB
- Valid dated records: 541,909
- Rows included in positive-sales analysis: 530,104
- Distinct countries in positive-sales analysis: 38
- Distinct invoices in positive-sales analysis: 19,960
- Distinct product codes in positive-sales analysis: 3,922

The dataset's recorded price units are retained; no currency conversion is performed.

## 5. System Architecture

```text
                   Online Retail CSV
                          |
                          v
                  Hadoop HDFS Input
                          |
                          v
                +-------------------+
                |    Hadoop Master  |
                |    NameNode       |
                |    ResourceManager|
                +-------------------+
                          |
                  YARN / MapReduce
                          |
              +-----------+-----------+
              |                       |
              v                       v
       +--------------+        +--------------+
       |   Worker 1   |        |   Worker 2   |
       |   DataNode   |        |   DataNode   |
       |   NodeManager|        |   NodeManager|
       +--------------+        +--------------+
              |                       |
              +-----------+-----------+
                          |
                          v
                 Python Mapper Tasks
                          |
                          v
                    Shuffle & Sort
                          |
                          v
                    Python Reducer
                          |
                          v
                  HDFS Aggregated Output
                          |
                          v
                  Python Analytics Script
                          |
                          v
                 13 Visualization Charts
```

The NameNode manages HDFS filesystem metadata, and the DataNodes store data blocks. YARN manages computing resources, while MapReduce performs the aggregation.

## 6. Project Structure

```text
BigData-Ecommerce-Analytics/
├── config/
│   └── hadoop/
│       ├── mapred-site.xml
│       └── yarn-site.xml
├── dataset/
│   └── raw/
│       └── online_retail.csv
├── src/
│   └── mapreduce/
│       ├── revenue_mapper.py
│       └── revenue_reducer.py
├── plots/
│   ├── 01_country_revenue.png
│   ├── 02_monthly_revenue.png
│   ├── 03_product_revenue.png
│   ├── 04_product_quantity.png
│   ├── 05_country_transactions.png
│   ├── 06_revenue_vs_transactions.png
│   ├── 07_monthly_invoice_volume.png
│   ├── 08_monthly_average_order_value.png
│   ├── 09_country_revenue_concentration.png
│   ├── 10_cancellation_invoice_trend.png
│   ├── 11_negative_quantity_trend.png
│   ├── 12_weekday_revenue.png
│   ├── 13_product_units_vs_revenue.png
│   └── analysis_summary.txt
├── analytics_plots.py
├── docker-compose.yml
├── test_reducer.txt
└── README.md
```

## 7. Hadoop Cluster Configuration

The project uses a three-node logical cluster running in Docker.

| Node | Responsibilities |
|---|---|
| `hadoop-master` | NameNode and YARN ResourceManager |
| `hadoop-worker1` | DataNode and NodeManager |
| `hadoop-worker2` | DataNode and NodeManager |

### Verify running containers

Run in PowerShell:

```powershell
docker ps
```

### Verify HDFS health

```powershell
docker exec hadoop-master bash -lc 'export JAVA_HOME=/usr/lib/jvm/jre; export HADOOP_HOME=/opt/hadoop; export HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop; hdfs dfsadmin -report'
```

Expected evidence from the project run:

- Two live DataNodes.
- Both worker nodes reported to the NameNode.
- HDFS reported healthy storage.
- The cluster was configured with a replication factor of 2.

The master and worker containers form the three-node cluster. The two DataNodes are the storage workers.

## 8. HDFS Data Storage

HDFS stores files as blocks and distributes block replicas across available DataNodes according to the replication policy.

### List the HDFS input directory

```powershell
docker exec hadoop-master bash -lc 'export JAVA_HOME=/usr/lib/jvm/jre; export HADOOP_HOME=/opt/hadoop; export HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop; hdfs dfs -ls /ecommerce/input'
```

### Check the dataset's HDFS integrity

```powershell
docker exec hadoop-master bash -lc 'export JAVA_HOME=/usr/lib/jvm/jre; export HADOOP_HOME=/opt/hadoop; export HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop; hdfs fsck /ecommerce/input/online_retail.csv -files -blocks -locations'
```

The project run reported:

- HDFS status: HEALTHY
- DataNodes: 2
- Input file size: 48,585,736 bytes
- Replication factor: 2
- Missing blocks: 0
- Corrupt blocks: 0

These checks demonstrate that the input file was available through HDFS and its block replicas were healthy.

## 9. MapReduce Implementation

### 9.1 Mapper: `revenue_mapper.py`

The mapper reads CSV records and extracts the country, quantity, and unit price.

For each processable transaction line, it calculates:

**Line-item revenue = Quantity × UnitPrice**

The mapper emits a country as the key and revenue as the value, separated by a tab.

Example input:

| Country | Quantity | Unit price |
|---|---:|---:|
| France | 2 | 10.00 |
| Germany | 3 | 5.00 |
| France | 4 | 10.00 |

Intermediate mapper output:

```text
France    20.00
Germany   15.00
France    40.00
```

The mapper skips the header, insufficient-column records, and rows with invalid numeric values. It does not perform the same cancellation and positive-sales filtering as the separate analytics script.

### 9.2 Shuffle and Sort

Hadoop groups mapper outputs by key so that the reducer receives values for the same country together.

Conceptually:

```text
France    [20.00, 40.00]
Germany   [15.00]
```

The MapReduce framework handles the intermediate data transfer, sorting, and grouping.

### 9.3 Reducer: `revenue_reducer.py`

The reducer adds the revenue values for each country and emits one aggregate total per country.

Example:

```text
France    60.00
Germany   15.00
```

This transforms individual transaction-line revenue values into country-level aggregates.

### 9.4 Hadoop Streaming

Hadoop Streaming allows the mapper and reducer to be written in Python while Hadoop manages task execution, intermediate data transfer, and job coordination.

The configured job uses:

- Input: `/ecommerce/input/online_retail.csv`
- Mapper: `revenue_mapper.py`
- Reducer: `revenue_reducer.py`
- Output: `/ecommerce/output/revenue_by_country`

### 9.5 Execute the MapReduce job

First, ensure that the Hadoop containers are running and that the Python scripts are available in the master container. If necessary, copy the scripts from the project root:

```powershell
docker cp .\src\mapreduce\revenue_mapper.py hadoop-master:/tmp/revenue_mapper.py
docker cp .\src\mapreduce\revenue_reducer.py hadoop-master:/tmp/revenue_reducer.py
```

Remove an existing output directory before rerunning the job, because Hadoop normally refuses to write into an existing output directory:

```powershell
docker exec hadoop-master bash -lc 'export JAVA_HOME=/usr/lib/jvm/jre; export HADOOP_HOME=/opt/hadoop; export HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop; hdfs dfs -rm -r -f /ecommerce/output/revenue_by_country'
```

Run Hadoop Streaming:

```powershell
docker exec hadoop-master bash -lc 'export JAVA_HOME=/usr/lib/jvm/jre; export HADOOP_HOME=/opt/hadoop; export HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop; hadoop jar /opt/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.6.jar -files /tmp/revenue_mapper.py,/tmp/revenue_reducer.py -mapper "python revenue_mapper.py" -reducer "python revenue_reducer.py" -input /ecommerce/input/online_retail.csv -output /ecommerce/output/revenue_by_country'
```

The output path must not already exist when the job starts.

### 9.6 Verify the result

List the output directory:

```powershell
docker exec hadoop-master bash -lc 'export JAVA_HOME=/usr/lib/jvm/jre; export HADOOP_HOME=/opt/hadoop; export HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop; hdfs dfs -ls /ecommerce/output/revenue_by_country'
```

Display the aggregated results:

```powershell
docker exec hadoop-master bash -lc 'export JAVA_HOME=/usr/lib/jvm/jre; export HADOOP_HOME=/opt/hadoop; export HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop; hdfs dfs -cat /ecommerce/output/revenue_by_country/part-*'
```

The successful execution produced a `_SUCCESS` marker and a `part-00000` result file.

## 10. Exploratory Data Analysis Using Python

The separate `analytics_plots.py` script reads the local CSV file using Pandas and generates additional metrics and visualizations using Matplotlib.

### Install dependencies

```powershell
python -m pip install pandas matplotlib
```

### Run the analysis

From the repository root:

```powershell
python analytics_plots.py
```

The script saves 13 PNG charts and `analysis_summary.txt` under the `plots/` directory.

### Sales filtering rules

The positive-sales analysis:

- Excludes invalid records missing required invoice, date, country, quantity, or price values.
- Excludes invoice identifiers beginning with `C`, which are cancellation-style identifiers in this dataset.
- Includes only records with positive quantities and positive unit prices.
- Calculates line-item revenue as quantity multiplied by unit price.
- Performs no currency conversion.

Negative-quantity records are examined separately and are not automatically treated as confirmed returns.

## 11. Visualizations and Their Business Value

| No. | Visualization | Purpose |
|---:|---|---|
| 1 | Country revenue | Identifies high-revenue markets |
| 2 | Monthly revenue | Shows changes in sales over time |
| 3 | Product revenue | Identifies products contributing the most revenue |
| 4 | Product quantity | Finds products with high sales volume |
| 5 | Country transactions | Compares invoice counts by country |
| 6 | Revenue vs. transactions | Compares revenue with transaction volume |
| 7 | Monthly invoice volume | Identifies changes in purchasing activity |
| 8 | Monthly average order value | Tracks average revenue per invoice |
| 9 | Country revenue concentration | Measures dependence on leading markets |
| 10 | Cancellation invoice trend | Examines cancellation-style invoice activity |
| 11 | Negative quantity trend | Explores negative-quantity records over time |
| 12 | Weekday revenue | Compares sales across weekdays |
| 13 | Product units vs. revenue | Compares product sales volume and revenue contribution |

## 12. Key Analytical Results

The following values were produced by the separate Python positive-sales analysis.

| Metric | Result |
|---|---:|
| Raw records | 541,909 |
| Rows included in positive-sales analysis | 530,104 |
| Countries represented | 38 |
| Distinct invoices | 19,960 |
| Distinct product codes | 3,922 |
| Positive-sales revenue | 10,666,684.54 |
| Top 10 countries' share of revenue | 97.21% |

### Top five countries by positive-sales revenue

| Country | Revenue |
|---|---:|
| United Kingdom | 9,025,222.084 |
| Netherlands | 285,446.340 |
| EIRE | 283,453.960 |
| Germany | 228,867.140 |
| France | 209,715.110 |

### Top five products by positive-sales revenue

| Product | Revenue |
|---|---:|
| DOTCOM POSTAGE | 206,248.77 |
| REGENCY CAKESTAND 3 TIER | 174,484.74 |
| PAPER CRAFT, LITTLE BIRDIE | 168,469.60 |
| WHITE HANGING HEART T-LIGHT HOLDER | 106,292.77 |
| PARTY BUNTING | 99,504.33 |

### Additional finding

The peak month in the positive-sales analysis was November 2011, with revenue of approximately 1,509,496.33.

These findings can help businesses understand geographic revenue concentration, product performance, seasonal demand, and transaction patterns.

**Metric consistency note:** The Hadoop mapper and reducer aggregate country revenue without applying all the positive-sales filters used by `analytics_plots.py`. For this reason, Hadoop output values and Python positive-sales totals can differ. The two results should not be presented as identical metrics.

## 13. Git and GitHub

Repository: https://github.com/SheilSheth/BigData-Ecommerce-Analytics

The repository contains the Hadoop configuration, mapper and reducer source code, Docker Compose configuration, analytical script, visualizations, and documentation.

Useful commands:

```powershell
git status
git log --oneline -5
git add README.md
git commit -m "Improve project documentation"
git push origin main
```

The raw dataset may be excluded from Git tracking to avoid committing the full data file.

## 14. Limitations

- The Hadoop MapReduce job currently aggregates line-item revenue by country; it does not implement all the filters used by the Python positive-sales analysis.
- The visualizations are generated locally by Pandas and Matplotlib rather than directly by Hadoop.
- The dataset is a historical snapshot, not a live e-commerce feed.
- The dataset's recorded price units are retained without currency conversion.
- The cluster is containerized for an academic demonstration; it is not a production deployment.
- The cluster uses two worker nodes, so the demonstration establishes a distributed setup but does not represent the scale of a large production cluster.

## 15. Future Improvements

- Apply consistent cancellation and invalid-record handling across Hadoop and Python analyses.
- Add additional MapReduce jobs for product rankings, monthly trends, and transaction counts.
- Compare the results of Hadoop processing with a validated local reference implementation.
- Introduce automated data validation and reproducible execution scripts.
- Expand the cluster with additional workers and test scalability.
- Build a dashboard to explore analytical results interactively.

## 16. Conclusion

This project demonstrates how Hadoop HDFS and MapReduce can be used to store and process e-commerce transaction data in a distributed environment. The Python mapper calculates line-item revenue, the reducer aggregates revenue by country, and HDFS stores the results.

A complementary Python analysis pipeline produces 13 visualizations and additional business metrics, making the findings easier to interpret.

The project combines distributed storage, distributed processing, data analysis, visualization, Docker-based cluster deployment, and Git-based version control in a single academic Big Data Analytics workflow.
