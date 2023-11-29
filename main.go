package main

import (
	"flag"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"path"

	"github.com/PuerkitoBio/goquery"
)

func main() {
	// parse command line arguments
	linkPtr := flag.String("link", "", "The URL of the page containing images")
	dirPtr := flag.String("dir", ".", "The directory to save images")
	flag.Parse()

	if *linkPtr == "" {
		fmt.Println("Please provide a valid URL using the -link flag.")
		return
	}

	// parse the URL
	u, err := url.Parse(*linkPtr)
	if err != nil {
		fmt.Println("Error parsing URL:", err)
		return
	}

	// fetch the HTML content
	resp, err := http.Get(u.String())
	if err != nil {
		fmt.Println("Error fetching URL:", err)
		return
	}
	defer resp.Body.Close()

	// parse HTML document
	doc, err := goquery.NewDocumentFromReader(resp.Body)
	if err != nil {
		fmt.Println("Error parsing HTML:", err)
		return
	}

	// create the directory if it doesn't exist
	err = os.MkdirAll(*dirPtr, os.ModePerm)
	if err != nil {
		fmt.Println("Error creating directory:", err)
		return
	}

	// extract and download images
	doc.Find("img").Each(func(i int, s *goquery.Selection) {
		src, exists := s.Attr("src")
		if exists {
			imgURL, err := url.Parse(src)
			if err != nil {
				fmt.Println("Error parsing image URL:", err)
				return
			}

			// check if the URL is relative
			if imgURL.Scheme == "" {
				// add the protocol (http or https) if it's missing
				imgURL.Scheme = u.Scheme
			}

			// download the image
			saveImagePath := path.Join(*dirPtr, path.Base(imgURL.Path))
			err = downloadImage(imgURL.String(), saveImagePath)
			if err != nil {
				fmt.Println("Error downloading image:", err)
				return
			}

			fmt.Printf("Downloaded: %s\n", saveImagePath)
		}
	})
}

func downloadImage(url, filePath string) error {
	// fetch the image
	resp, err := http.Get(url)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	// create the file
	file, err := os.Create(filePath)
	if err != nil {
		return err
	}
	defer file.Close()

	// copy the image data to the file
	_, err = io.Copy(file, resp.Body)
	if err != nil {
		return err
	}

	return nil
}
