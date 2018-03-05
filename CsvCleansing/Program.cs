using HtmlAgilityPack;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.IO;
using System.Text.RegularExpressions;

namespace CsvCleansing
{
    public class IncidentRec
    {
        public int FileId { get; set; }
        public string GeneralIncidentType { get; set; }
        public string SpecificIncidentType { get; set; }
        public string Severity { get; set; }
        public string Description { get; set; }
    }

    class Program
    {
        static List<string> AllKnownCats = new List<string>();
        static bool IsFirstLine(string line)
        {
            if(!string.IsNullOrEmpty(line))
            {
                int n = line.IndexOf(",");
                if ( n > 0)
                {
                    string id = line.Substring(0, n - 1);
                    return int.TryParse(id, out int m);
                }                
            }
            return false;
        }

        static string FilterHtml(string rawDescription)
        {
            /*
            var doc = new HtmlDocument();
            doc.LoadHtml(rawDescription);
            var result = doc.DocumentNode.InnerText;
            */
            string decode = System.Web.HttpUtility.HtmlDecode(rawDescription);
            Regex objRegExp = new Regex("<(.|\n)+?>");
            string replace = objRegExp.Replace(decode, "");
            replace = replace.Replace("\\n", " ");
            return replace.Trim("\t\r\n ".ToCharArray());
        }

        static IncidentRec ParseBuffer(List<string> buffer)
        {
            if(buffer.Count > 0)
            {
                string firstLine = buffer[0];
                int n1 = firstLine.IndexOf(",");
                if ( n1 > 0 )
                {
                    int n2 = firstLine.IndexOf(",", n1 + 1);
                    if( n2 >  0)
                    {
                        int n3 = firstLine.IndexOf(",", n2 + 1);
                        if( n3 > 0 )
                        {
                            int n4 = firstLine.IndexOf(",", n3 + 1);
                            if( n4 > 0 )
                            {
                                string sid = firstLine.Substring(0, n1);
                                string sGIT = firstLine.Substring(n1 + 1, n2 - n1 -1 ).Trim();
                                string sSIT = firstLine.Substring(n2 + 1, n3 - n2 - 1).Trim();
                                string sSev = firstLine.Substring(n3 + 1, n4 - n3 - 1).Trim();
                                string sTemp = firstLine.Substring(n4 + 1);
                                for(int i = 1; i< buffer.Count; i++)
                                {
                                    sTemp += "\n" + buffer[i];
                                }

                                var result = new IncidentRec();
                                result.FileId = int.Parse(sid);
                                if(!AllKnownCats.Contains(sGIT))
                                {
                                    AllKnownCats.Add(sGIT);
                                }
                                result.GeneralIncidentType = sGIT;
                                if (!AllKnownCats.Contains(sSev))
                                {
                                    AllKnownCats.Add(sSev);
                                }
                                result.Severity = sSev;
                                result.Description = FilterHtml(sTemp);
                                return result;
                            }
                        }
                    }
                }
            }
            return null;
        }

        static void Main(string[] args)
        {
            string csvInputFileName = "C:\\Backup\\DataN1.csv";
            var allLines = System.IO.File.ReadAllLines(csvInputFileName);

            List<IncidentRec> results = new List<IncidentRec>();
            Console.WriteLine("Parsing");
            List<string> thisItemLines = new List<string>();
            for(int i = 1; i < allLines.Length; i++ )
            {
                string temp = allLines[i];
                if (string.IsNullOrEmpty(temp))
                {
                    if ( thisItemLines.Count > 0 )
                    {
                        var result = ParseBuffer(thisItemLines);
                        if (result != null)
                        {
                            results.Add(result);
                        }
                        thisItemLines.Clear();
                    }
                 }
                else
                {
                    thisItemLines.Add(temp);
                }
            }

            using(StreamWriter sw = File.CreateText("C:\\Backup\\DataNV1.json"))
            {
                JsonSerializer serializer = new JsonSerializer();
                serializer.Formatting = Formatting.Indented;
                serializer.Serialize(sw, results);
            }
            File.WriteAllLines("c:\\backup\\allCats.txt", AllKnownCats.ToArray());
            Console.WriteLine("Done");
            Console.ReadKey();
        }
    }
}
