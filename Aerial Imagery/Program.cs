using System;
using BingMapsRESTToolkit;
using System.Net;

//Written by David Bednarczuk (IIT 2021)

//A Bounding Box Object takes in parameters = S. Lat, W. Long, N. Lat., and E. Long.

//IIT Campus: 41.831, -87.629, 41.839, -87.623
//White House: 38.895418, -77.039247, 38.898689, -77.033857
//The Lourve: 48.857565, 2.323465, 48.866363, 2.339198
//Hobbiton: -37.859088, 175.678088, -37.856788, 175.682430

namespace SatMapProjectOne
{
    class Program
    {
        //Initializes BoundingBox and Uri, Downloads .png of URL request to bin folder
        public Program(string key, double[] arr)
        {
            BoundingBox iitCampus = new BoundingBox(arr);
            Uri imURL = new Uri(getMapURL(key, iitCampus));

            WebClient wc = new WebClient();
            wc.DownloadFile(imURL, "hobbiton.png");
        }
       
        //Method that returns a Aerial Imagery URL
        public string getMapURL(string key, BoundingBox iitCampus)
        {
            ImageryRequest i = new ImageryRequest();
            i.BingMapsKey = key;                                                                   //Bing Maps Rest API Key
            i.MapArea = iitCampus;                                                                 //Bounding Box
            i.MapHeight = 10000;
            i.MapWidth = 10000;
            Console.WriteLine(i.GetPostRequestUrl());

            return i.GetPostRequestUrl();
        }

        static void Main(string[] args)
        {
            string key = "AnF6Y78C0Vk9WxjTmkyaYNHz6TQWX-QI7uZyh59LTZvDua7Rbw39WzgAfKNz_FGm";
            //double[] bbox = { 41.831173, -87.629539, 41.839406, -87.623453 };                    //IIT Campus
            //double[] bbox = { 38.895418, -77.039247, 38.898689, -77.033857 };                    //Whitehouse Lawn
            //double[] bbox = { 48.857565, 2.323465, 48.866363, 2.339198 };                        //Louvre Museum
            double[] bbox = { -37.859088, 175.678088, -37.856788, 175.682430 };                  //Hobbiton

            Program pro = new Program(key, bbox);
        }
    }
}
